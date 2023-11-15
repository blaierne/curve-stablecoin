certoraRun contracts/Controller.vy \
    --verify Controller:certora/specs/Controller.spec \
    --loop_iter 3 \
    --optimistic_loop \
    --process evm \
    --wait_for_results \
    --msg "Controller" --server production --coverage_info basic --debug --prover_version mike/CERT-3866-vyper-parse


# certoraRun.py certora/configs/Sanity-Controller.conf --debug --server production --coverage_info basic --prover_version mike/CERT-3866-vyper-parse --loop_iter 5