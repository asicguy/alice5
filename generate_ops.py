
# Generates C++ include files for the SPIR-V instructions.

import sys
import json
import re

HEADER = "#ifndef %s\n#define %s\n\n// Automatically generated by generate_ops.py. DO NOT EDIT.\n\n"
FOOTER = "\n#endif // %s\n"
IMPL_RE = re.compile(r"void Interpreter::step(.*)\(const Insn(.*)& insn\)")

# Instruction operand (with some of our own info).
class Operand:
    def __init__(self, json_operand, operand_kind_map, operand_index, instruction_name):
        kind = json_operand["kind"]
        name = json_operand.get("name")
        quantifier = json_operand.get("quantifier")

        cpp_type = "uint32_t"
        cpp_name = cleanUpName(name) + "Id" if name else None
        decode_function = "nextu"
        default_value = ""

        if kind == "IdResultType":
            assert(not name)
            cpp_name = "type"
            cpp_comment = "result type"
        elif kind == "IdResult":
            assert(not name)
            cpp_name = "resultId"
            cpp_comment = "SSA register for result value"
        elif kind == "IdRef":
            assert(name)
            cpp_comment = "operand from register"
        elif kind == "LiteralString":
            cpp_type = "std::string"
            cpp_comment = "literal string"
            decode_function = "nexts"
        else:
            operand_kind = operand_kind_map[kind]
            category = operand_kind["category"]
            if category in ["Literal", "Composite", "Id"]:
                # We've already handled literal strings above. All
                # composites and IDs are integers.
                assert(cpp_name)
                cpp_comment = kind
            elif category in ["ValueEnum", "BitEnum"]:
                # Keep uint32_t.
                if not cpp_name:
                    cpp_name = CamelCase_to_camelCase(kind)
                cpp_comment = kind
            else:
                sys.stderr.write("Unhandled kind \"%s\" for operator \"%s\".\n" % (kind, opname))
                sys.exit(1)

        # Varargs.
        if quantifier == "*":
            cpp_type = "std::vector<" + cpp_type + ">"
            decode_function = "restv"

        if kind == "MemoryAccess":
            default_value = "NO_MEMORY_ACCESS_SEMANTIC"

        # Should have a default if it's optional.
        if quantifier == "?" and not default_value:
            sys.stderr.write("Warning: No default for optional operand %d of %s.\n"
                    % (operand_index + 1, instruction_name))

        self.kind = kind
        self.name = name
        self.quantifier = quantifier
        self.cpp_type = cpp_type
        self.cpp_name = cpp_name
        self.cpp_comment = cpp_comment
        self.decode_function = decode_function
        self.default_value = default_value

def CamelCase_to_camelCase(name):
    return name[0].lower() + name[1:]

# Clean up a name like "'Sampled Image'" to "sampledImage".
def cleanUpName(name):
    if "," in name:
        return "operand"
    else:
        return CamelCase_to_camelCase(name[1:-1].replace(" ", "").replace("~", ""))

# Figure out what instructions are already implemented.
def get_already_implemented_instructions(source_pathname):
    lines = open(source_pathname).readlines()

    already_implemented = set()

    for line in lines:
        m = IMPL_RE.match(line.strip())
        if m:
            # Make sure the function name and parameter match.
            name1 = m.group(1)
            name2 = m.group(2)
            assert(name1 == name2)

            already_implemented.add(name1)

    return already_implemented

def main():
    # Input file.
    json_pathname = sys.argv[1]
    grammar = json.load(open(json_pathname))

    glsl_std_450_json_pathname = sys.argv[2]
    glsl_std_450_grammar = json.load(open(glsl_std_450_json_pathname))

    # Create map from operand kind name ("FPFastMathMode") to info about the kind.
    operand_kind_map = dict((kind["kind"], kind) for kind in grammar["operand_kinds"])

    # Find what instructions have already been implemented.
    already_implemented = get_already_implemented_instructions("shade.cpp")

    # Output files.
    opcode_to_string_f = open("opcode_to_string.h", "w")
    opcode_to_string_f.write(HEADER % ("OPCODE_TO_STRING_H", "OPCODE_TO_STRING_H"));

    GLSLstd450_opcode_to_string_f = open("GLSLstd450_opcode_to_string.h", "w")
    GLSLstd450_opcode_to_string_f.write(HEADER % ("GLSLSTD450_OPCODE_TO_STRING_H", "GLSLSTD450_OPCODE_TO_STRING_H"));

    opcode_structs_f = open("opcode_structs.h", "w")
    opcode_structs_f.write(HEADER % ("OPCODE_STRUCTS_H", "OPCODE_STRUCTS_H"));
    opcode_structs_f.write("#include \"interpreter.h\"\n\n")

    opcode_struct_decl_f = open("opcode_struct_decl.h", "w")
    opcode_struct_decl_f.write(HEADER % ("OPCODE_STRUCT_DECL_H", "OPCODE_STRUCT_DECL_H"));

    opcode_impl_f = open("opcode_impl.h", "w")
    opcode_impl_f.write(HEADER % ("OPCODE_IMPL_H", "OPCODE_IMPL_H"));

    opcode_decl_f = open("opcode_decl.h", "w")
    opcode_decl_f.write(HEADER % ("OPCODE_DECL_H", "OPCODE_DECL_H"));

    opcode_decode_f = open("opcode_decode.h", "w")
    opcode_decode_f.write(HEADER % ("OPCODE_DECODE_H", "OPCODE_DECODE_H"));

    # Output instructions for core SPIR-V
    for instruction in grammar["instructions"]:
        opcode = instruction["opcode"]
        opname = instruction["opname"]
        if not opname.startswith("Op"):
            sys.stderr.write("Instruction name \"%s\" does not start with \"Op\".\n" % opname);
            sys.exit(1)

        short_opname = opname[2:]
        struct_opname = "Insn" + short_opname

        # Process the operands, adding our own custom fields to them.
        operands = [Operand(json_operand, operand_kind_map, operand_index, opname)
                for operand_index, json_operand in enumerate(instruction.get("operands", []))]

        # Opcode to string file.
        opcode_to_string_f.write("    {%d, \"%s\"},\n" % (opcode, short_opname))

        if short_opname in already_implemented:
            # Struct file.
            opcode_structs_f.write("// %s instruction (code %d).\n" % (opname, opcode))
            opcode_structs_f.write("struct %s : public Instruction {\n" % (struct_opname, ))
            params = []
            inits = []
            for operand in operands:
                params.append("%s %s" % (operand.cpp_type, operand.cpp_name))
                inits.append("%s(%s)" % (operand.cpp_name, operand.cpp_name))
            opcode_structs_f.write("    %s(%s)%s%s {}\n" %
                    (struct_opname,
                        ", ".join(params),
                        " : " if params else "",
                        ", ".join(inits)))
            for operand in operands:
                opcode_structs_f.write("    %s %s; // %s%s\n" % (operand.cpp_type,
                    operand.cpp_name, operand.cpp_comment,
                    " (optional)" if operand.quantifier == "?" else ""));
            opcode_structs_f.write("    virtual void step(Interpreter *interpreter) { interpreter->step%s(*this); }\n" % short_opname)
            opcode_structs_f.write("};\n\n")

            # Struct declaration file.
            opcode_struct_decl_f.write("struct %s;\n" % (struct_opname, ))

            # Decode file.
            opcode_decode_f.write("case Spv%s: {\n" % opname)
            for operand in operands:
                opcode_decode_f.write("    %s %s = %s(%s);\n" %
                        (operand.cpp_type, operand.cpp_name,
                            operand.decode_function, operand.default_value))
            opcode_decode_f.write("    pgm->code.push_back(new %s{%s});\n" %
                    (struct_opname, ", ".join(operand.cpp_name for operand in operands)))
            if 'IdResultType' in [op.kind for op in operands] and 'IdResult' in [op.kind for op in operands]:
                opcode_decode_f.write("    pgm->resultsCreated[resultId] = type;\n")
                
            opcode_decode_f.write("    if(pgm->verbose) {\n")
            opcode_decode_f.write("        std::cout << \"%s\";\n" % short_opname)
            for operand in operands:
                opcode_decode_f.write("        std::cout << \" %s \";\n" % operand.cpp_name)
                if operand.quantifier == "*":
                    opcode_decode_f.write("        for(int i = 0; i < %s.size(); i++)\n"
                            % operand.cpp_name)
                    opcode_decode_f.write("            std::cout << %s[i] << \" \";\n" % operand.cpp_name)
                else:
                    opcode_decode_f.write("        std::cout << %s;\n" % operand.cpp_name)
            opcode_decode_f.write("        std::cout << \"\\n\";\n")
            opcode_decode_f.write("    }\n")
            opcode_decode_f.write("    break;\n")
            opcode_decode_f.write("}\n\n")

            # Declaration file.
            opcode_decl_f.write("void step%s(const %s& insn);\n" % (short_opname, struct_opname))

        # Generate a stub if it's not already implemented in the C++ file.
        if short_opname not in already_implemented:
            opcode_impl_f.write("void Interpreter::step%s(const %s& insn)\n{\n    std::cerr << \"step%s() not implemented\\n\";\n}\n\n"
                    % (short_opname, struct_opname, short_opname))

    # Emit opcode decode preamble for extinst
    opcode_decode_f.write("case SpvOpExtInst: {\n")
    opcode_decode_f.write("    uint32_t type = nextu();\n")
    opcode_decode_f.write("    uint32_t resultId = nextu();\n")
    opcode_decode_f.write("    uint32_t ext = nextu();\n")
    opcode_decode_f.write("    uint32_t opcode = nextu();\n")
    opcode_decode_f.write("    if(ext == pgm->ExtInstGLSL_std_450_id) {\n")
    opcode_decode_f.write("        switch(opcode) {\n")

    type_json_operand = {"kind" : "IdResultType" }
    resultid_json_operand = { "kind" : "IdResult" }
    for instruction in glsl_std_450_grammar["instructions"]:
        opcode = instruction["opcode"]
        opname = "GLSLstd450" + instruction["opname"]
        struct_opname = "Insn" + opname

        # Set up 2 operands from OpExtInst that are handled by the extension instruction
        extinst_operands = [Operand(type_json_operand, operand_kind_map, 0, opname), Operand(resultid_json_operand, operand_kind_map, 1, opname)]

        # Process the operands, adding our own custom fields to them.
        operands = [Operand(json_operand, operand_kind_map, operand_index, opname)
                for operand_index, json_operand in enumerate(instruction.get("operands", []))]

        # Opcode to string file.
        GLSLstd450_opcode_to_string_f.write("    {%d, \"%s\"},\n" % (opcode, opname))

        if opname in already_implemented:
            # Struct file.
            opcode_structs_f.write("// %s instruction (code %d).\n" % (opname, opcode))
            opcode_structs_f.write("struct %s : public Instruction {\n" % (struct_opname, ))
            params = []
            inits = []
            for operand in extinst_operands + operands:
                params.append("%s %s" % (operand.cpp_type, operand.cpp_name))
                inits.append("%s(%s)" % (operand.cpp_name, operand.cpp_name))
            opcode_structs_f.write("    %s(%s)%s%s {}\n" %
                    (struct_opname,
                        ", ".join(params),
                        " : " if params else "",
                        ", ".join(inits)))
            for operand in extinst_operands + operands:
                opcode_structs_f.write("    %s %s; // %s%s\n" % (operand.cpp_type,
                    operand.cpp_name, operand.cpp_comment,
                    " (optional)" if operand.quantifier == "?" else ""));
            opcode_structs_f.write("    virtual void step(Interpreter *interpreter) { interpreter->step%s(*this); }\n" % opname)
            opcode_structs_f.write("};\n\n")

            # Struct declaration file.
            opcode_struct_decl_f.write("struct %s;\n" % (struct_opname, ))

            # Decode file.
            opcode_decode_f.write("case %s: {\n" % opname)
            for operand in operands:
                opcode_decode_f.write("    %s %s = %s(%s);\n" %
                        (operand.cpp_type, operand.cpp_name,
                            operand.decode_function, operand.default_value))
            opcode_decode_f.write("    pgm->code.push_back(new %s{%s});\n" %
                    (struct_opname, ", ".join(operand.cpp_name for operand in extinst_operands + operands)))
            opcode_decode_f.write("    pgm->resultsCreated[resultId] = type;\n")
            opcode_decode_f.write("    if(pgm->verbose) {\n")
            opcode_decode_f.write("        std::cout << \"%s\";\n" % opname)
            for operand in extinst_operands + operands:
                opcode_decode_f.write("        std::cout << \" %s \";\n" % operand.cpp_name)
                if operand.quantifier == "*":
                    opcode_decode_f.write("        for(int i = 0; i < %s.size(); i++)\n"
                            % operand.cpp_name)
                    opcode_decode_f.write("            std::cout << %s[i] << \" \";\n" % operand.cpp_name)
                else:
                    opcode_decode_f.write("        std::cout << %s;\n" % operand.cpp_name)
            opcode_decode_f.write("        std::cout << \"\\n\";\n")
            opcode_decode_f.write("    }\n")
            opcode_decode_f.write("    break;\n")
            opcode_decode_f.write("}\n\n")

            # Declaration file.
            opcode_decl_f.write("void step%s(const %s& insn);\n" % (opname, struct_opname))

        # Generate a stub if it's not already implemented in the C++ file.
        if opname not in already_implemented:
            opcode_impl_f.write("void Interpreter::step%s(const %s& insn)\n{\n    std::cerr << \"step%s() not implemented\\n\";\n}\n\n"
                    % (opname, struct_opname, opname))

    opcode_decode_f.write("            default: {\n")
    opcode_decode_f.write("                if(pgm->throwOnUnimplemented) {\n")
    opcode_decode_f.write("                    throw std::runtime_error(\"unimplemented GLSLstd450 opcode \" + GLSLstd450OpcodeToString[opcode] + \" (\" + std::to_string(opcode) + \")\");\n")
    opcode_decode_f.write("                } else {\n")
    opcode_decode_f.write("                    std::cout << \"unimplemented GLSLstd450 opcode \" << GLSLstd450OpcodeToString[opcode] << \" (\" << opcode << \")\\n\";\n")
    opcode_decode_f.write("                    pgm->hasUnimplemented = true;\n")
    opcode_decode_f.write("                }\n")
    opcode_decode_f.write("                break;\n")
    opcode_decode_f.write("            }\n")
    opcode_decode_f.write("        }\n")
    opcode_decode_f.write("    } else {\n")
    opcode_decode_f.write("        throw std::runtime_error(\"unimplemented instruction \" + std::to_string(opcode) + \" from extension set \" + std::to_string(ext));\n")
    opcode_decode_f.write("    }\n")
    opcode_decode_f.write("    break;\n")
    opcode_decode_f.write("}\n")

    opcode_to_string_f.write(FOOTER % "OPCODE_TO_STRING_H");
    GLSLstd450_opcode_to_string_f.write(FOOTER % "GLSLSTD450_OPCODE_TO_STRING_H");
    opcode_structs_f.write(FOOTER % "OPCODE_STRUCTS_H");
    opcode_struct_decl_f.write(FOOTER % "OPCODE_STRUCT_DECL_H");
    opcode_impl_f.write(FOOTER % "OPCODE_IMPL_H");
    opcode_decl_f.write(FOOTER % "OPCODE_DECL_H");
    opcode_decode_f.write(FOOTER % "OPCODE_DECODE_H");

    opcode_to_string_f.close()
    GLSLstd450_opcode_to_string_f.close()
    opcode_structs_f.close()
    opcode_struct_decl_f.close()
    opcode_impl_f.close()
    opcode_decode_f.close()
    opcode_decl_f.close()

if __name__ == "__main__":
    main()

