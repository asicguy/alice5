#ifndef OPCODE_DECL_H
#define OPCODE_DECL_H

// Automatically generated by generate_ops.py. DO NOT EDIT.

void stepNop(const InsnNop& insn);
void stepFunctionParameter(const InsnFunctionParameter& insn);
void stepFunctionCall(const InsnFunctionCall& insn);
void stepLoad(const InsnLoad& insn);
void stepStore(const InsnStore& insn);
void stepAccessChain(const InsnAccessChain& insn);
void stepVectorShuffle(const InsnVectorShuffle& insn);
void stepCompositeConstruct(const InsnCompositeConstruct& insn);
void stepCompositeExtract(const InsnCompositeExtract& insn);
void stepCompositeInsert(const InsnCompositeInsert& insn);
void stepImageSampleImplicitLod(const InsnImageSampleImplicitLod& insn);
void stepConvertFToS(const InsnConvertFToS& insn);
void stepConvertSToF(const InsnConvertSToF& insn);
void stepFNegate(const InsnFNegate& insn);
void stepIAdd(const InsnIAdd& insn);
void stepFAdd(const InsnFAdd& insn);
void stepFSub(const InsnFSub& insn);
void stepFMul(const InsnFMul& insn);
void stepSDiv(const InsnSDiv& insn);
void stepFDiv(const InsnFDiv& insn);
void stepFMod(const InsnFMod& insn);
void stepVectorTimesScalar(const InsnVectorTimesScalar& insn);
void stepVectorTimesMatrix(const InsnVectorTimesMatrix& insn);
void stepMatrixTimesVector(const InsnMatrixTimesVector& insn);
void stepDot(const InsnDot& insn);
void stepLogicalOr(const InsnLogicalOr& insn);
void stepLogicalNot(const InsnLogicalNot& insn);
void stepSelect(const InsnSelect& insn);
void stepIEqual(const InsnIEqual& insn);
void stepSLessThan(const InsnSLessThan& insn);
void stepSLessThanEqual(const InsnSLessThanEqual& insn);
void stepFOrdEqual(const InsnFOrdEqual& insn);
void stepFOrdLessThan(const InsnFOrdLessThan& insn);
void stepFOrdGreaterThan(const InsnFOrdGreaterThan& insn);
void stepFOrdLessThanEqual(const InsnFOrdLessThanEqual& insn);
void stepFOrdGreaterThanEqual(const InsnFOrdGreaterThanEqual& insn);
void stepPhi(const InsnPhi& insn);
void stepBranch(const InsnBranch& insn);
void stepBranchConditional(const InsnBranchConditional& insn);
void stepReturn(const InsnReturn& insn);
void stepReturnValue(const InsnReturnValue& insn);
void stepGLSLstd450FAbs(const InsnGLSLstd450FAbs& insn);
void stepGLSLstd450FSign(const InsnGLSLstd450FSign& insn);
void stepGLSLstd450Floor(const InsnGLSLstd450Floor& insn);
void stepGLSLstd450Fract(const InsnGLSLstd450Fract& insn);
void stepGLSLstd450Radians(const InsnGLSLstd450Radians& insn);
void stepGLSLstd450Sin(const InsnGLSLstd450Sin& insn);
void stepGLSLstd450Cos(const InsnGLSLstd450Cos& insn);
void stepGLSLstd450Atan(const InsnGLSLstd450Atan& insn);
void stepGLSLstd450Atan2(const InsnGLSLstd450Atan2& insn);
void stepGLSLstd450Pow(const InsnGLSLstd450Pow& insn);
void stepGLSLstd450Exp(const InsnGLSLstd450Exp& insn);
void stepGLSLstd450Exp2(const InsnGLSLstd450Exp2& insn);
void stepGLSLstd450FMin(const InsnGLSLstd450FMin& insn);
void stepGLSLstd450FMax(const InsnGLSLstd450FMax& insn);
void stepGLSLstd450FClamp(const InsnGLSLstd450FClamp& insn);
void stepGLSLstd450FMix(const InsnGLSLstd450FMix& insn);
void stepGLSLstd450Step(const InsnGLSLstd450Step& insn);
void stepGLSLstd450SmoothStep(const InsnGLSLstd450SmoothStep& insn);
void stepGLSLstd450Length(const InsnGLSLstd450Length& insn);
void stepGLSLstd450Distance(const InsnGLSLstd450Distance& insn);
void stepGLSLstd450Cross(const InsnGLSLstd450Cross& insn);
void stepGLSLstd450Normalize(const InsnGLSLstd450Normalize& insn);
void stepGLSLstd450Reflect(const InsnGLSLstd450Reflect& insn);
void stepGLSLstd450Refract(const InsnGLSLstd450Refract& insn);

#endif // OPCODE_DECL_H
