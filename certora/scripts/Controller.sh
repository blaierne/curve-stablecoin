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
    --rule_sanity \
    --msg "Controller all" --server production --prover_version shelly/vyperlinking \
    --prover_args '-tmpOptAllGhostsAreGlobal true -canonicalizeTAC false' 
