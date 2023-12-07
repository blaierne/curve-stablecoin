certoraRun contracts/Controller.vy certora/mocs/Stablecoin.vy contracts/AMM.vy certora/mocs/FactoryMock.vy \
    certora/mocs/WETH.vy certora/mocs/CollateralToken.vy \
    --verify Controller:certora/specs/Controller.spec \
    --link Controller:STABLECOIN=Stablecoin \
    --link Controller:COLLATERAL_TOKEN=CollateralToken \
    --link Controller:AMM=AMM \
    --loop_iter 3 \
    --optimistic_loop \
    --process evm \
    --wait_for_results \
    --msg "Controller" --server production --coverage_info basic --prover_version shelly/cert4266bigintslots
