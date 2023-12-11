certoraRun contracts/Stableswap.vy \
    --verify Stableswap:certora/specs/Stableswap.spec \
    --loop_iter 3 \
    --optimistic_loop \
    --process evm \
    --wait_for_results \
    --msg "Stableswap - ERC rules" \
    --prover_args '-smt_bitVectorTheory true -smt_hashingScheme plainInjectivity' \
    --server production