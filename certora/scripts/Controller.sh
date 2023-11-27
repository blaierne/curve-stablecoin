certoraRun contracts/Controller.vy certora/mocs/Stablecoin.vy contracts/AMM.vy \
    --verify Controller:certora/specs/Controller.spec \
    --link Controller:STABLECOIN=Stablecoin \
    --link Controller:AMM=AMM \
    --loop_iter 3 \
    --optimistic_loop \
    --process evm \
    --wait_for_results \
    --msg "Controller" --server production --coverage_info basic
