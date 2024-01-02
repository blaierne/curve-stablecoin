certoraRun contracts/Controller.vy certora/mocs/Stablecoin.vy contracts/AMM.vy certora/mocs/FactoryMock.vy \
    certora/mocs/WETH.vy certora/mocs/CollateralToken.vy \
    --verify Controller:certora/specs/Controller.spec \
    --link Controller:STABLECOIN=Stablecoin \
    --link Controller:COLLATERAL_TOKEN=CollateralToken \
    --link Controller:AMM=AMM \
    --link AMM:COLLATERAL_TOKEN=CollateralToken \
    --link Controller:FACTORY=FactoryMock \
    --loop_iter 3 \
    --optimistic_loop \
    --process evm \
    --rule_sanity \
    --msg "Controller $1" --server production --prover_version shelly/mergedvyperwithjohn \
    --prover_args '-tmpOptAllGhostsAreGlobal true -canonicalizeTAC false -enableMemorySplit false -enableSolidityBasedInlining false -optimisticFallback true' --rule $1
