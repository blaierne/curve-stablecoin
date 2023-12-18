certoraRun contracts/Stablecoin.vy \
    --verify Stablecoin:certora/specs/Stablecoin.spec \
    --loop_iter 3 \
    --optimistic_loop \
    --process evm \
    --wait_for_results \
    --msg "Stablecoin" 