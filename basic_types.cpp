
#include <iomanip>

#include "basic_types.h"
#include "function.h"
#include "risc-v.h"
#include "program.h"

// Compute successor instructions.
std::vector<Instruction *> Instruction::succ() const {
    std::vector<Instruction *> instructions;

    if (next) {
        // Not at end of block, just return next instruction.
        instructions.push_back(next.get());
    } else {
        // At end of block. Follow the block's successors.
        assert(list != nullptr);
        assert(list->block != nullptr);
        assert(list->block->function != nullptr);

        for (uint32_t blockId : list->block->succ) {
            Block *block = list->block->function->blocks.at(blockId).get();
            instructions.push_back(block->instructions.head.get());
        }
    }

    return instructions;
}

// Compute predecessor instructions.
std::vector<Instruction *> Instruction::pred() const {
    std::vector<Instruction *> instructions;

    if (prev) {
        // Not at beginning of block, just return previous instruction.
        instructions.push_back(prev.get());
    } else {
        // At beginning of block. Follow the block's predecessors.
        assert(list != nullptr);
        assert(list->block != nullptr);
        assert(list->block->function != nullptr);

        for (uint32_t blockId : list->block->pred) {
            Block *block = list->block->function->blocks.at(blockId).get();
            instructions.push_back(block->instructions.tail.get());
        }
    }

    return instructions;
}

uint32_t Instruction::blockId() const {
    return list->block->blockId;
}

std::string Instruction::pos() const {
    std::ostringstream ss;

    if (list == nullptr) {
        ss << "not in a block";
    } else {
        ss << list->block->blockId << "@";

        // Find the index in the block.
        bool found = false;
        int index;
        std::shared_ptr<Instruction> other;
        for (index = 0, other = list->head; other && !found; index++, other = other->next) {
            if (other.get() == this) {
                ss << index;
                found = true;
            }
        }
        assert(found);
    }

    return ss.str();
}

// Swap the two instruction lists.
void swap(InstructionList &a, InstructionList &b) {
    a.swap(b);
}
