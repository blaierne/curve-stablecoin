using Stablecoin as stablecoin;
using CollateralToken as collateraltoken;
using AMM as amm;
using FactoryMock as factory;
using WETH as weth;

methods {
    // view:
    function factory() external returns (address) envfree;
    function amm() external returns (address) envfree;
    function collateral_token() external returns (address) envfree;
    function debt(address) external returns (uint256) envfree;
    function loan_exists(address) external returns (bool) envfree;
    function total_debt() external returns (uint256) envfree;
    function max_borrowable(uint256, uint256, uint256) external returns (uint256) envfree;
    function calculate_debt_n1(uint256, uint256, uint256) external returns (int256) envfree;

    function create_loan(uint256, uint256, uint256) external; // payable nonreentrant
    // function function create_loan_extended(uint256, uint256, uint256, address, DynArray[uint256,5]) external; // payable nonreentrant
    function add_collateral(uint256, address) external; // payable nonreentrant
    function remove_collateral(uint256, bool) external; // nonreentrant
    function borrow_more(uint256, uint256) external; // payable nonreentrant
    function repay(uint256, address, int256, bool) external; // nonreentrant
    // function repay_extended(address, DynArray[uint256,5]) external;
    function health_calculator(address, int256, int256, bool, uint256) external returns (int256) envfree; // view
    function liquidate(address, uint256, bool) external;
    // function liquidate_extended(address, uint256, uint256, bool, address, DynArray[uint256,5]) external;
    function tokens_to_liquidate(address, uint256) external returns (uint256);
    function health(address, bool) external returns (int256) envfree;
    function amm_price() external returns (uint256) envfree;
    function user_prices(address) external returns (uint256[2]) envfree;
    function user_state(address) external returns (uint256[4]) envfree;
    function set_amm_fee(uint256) external;
    function set_amm_admin_fee(uint256) external;
    function set_monetary_policy(address) external;
    function set_borrowing_discounts(uint256, uint256) external;
    function set_callback(address) external;
    function admin_fees() external returns (uint256) envfree;
    function collect_fees() external returns (uint256) envfree;

    // Controller Getters:
    function minted() external returns (uint256) envfree;
    function redeemed() external returns (uint256) envfree;
    function AMM() external returns (address) envfree;

    // ControllerHarness:
    function get_initial_debt(address) external returns (uint256) envfree;
    function get_rate_mul(address) external returns (uint256) envfree;

    // AMM:
    function AMM.A() external returns (uint256);
    function AMM.get_p() external returns (uint256);
    function AMM.get_base_price() external returns (uint256);
    function AMM.active_band() external returns (int256);
    function AMM.active_band_with_skip() external returns (int256);
    function AMM.p_oracle_up(int256) external returns (uint256);
    function AMM.p_oracle_down(int256) external returns (uint256);
    function AMM.deposit_range(address, uint256, int256, int256) external;
    function AMM.read_user_tick_numbers(address) external returns (int256[2]);
    function AMM.get_sum_xy(address) external returns (uint256[2]);
    function AMM.withdraw(address, uint256) external returns (uint256[2]); // nonpayable
    function AMM.get_x_down(address) external returns (uint256);
    function AMM.get_rate_mul() external returns (uint256);
    function AMM.set_rate(uint256) external returns (uint256); // nonpayable
    function AMM.set_fee(uint256) external; // nonpayable
    function AMM.set_admin_fee(uint256) external; // nonpayable
    function AMM.price_oracle() external returns (uint256);
    function AMM.can_skip_bands(int256) external returns (bool);
    // function set_price_oracle(PriceOracle) external; // nonpayable
    function AMM.admin_fees_x() external returns (uint256) envfree;
    function AMM.admin_fees_y() external returns (uint256) envfree;
    function AMM.reset_admin_fees() external; // nonpayable
    function AMM.has_liquidity(address) external returns (bool);
    function AMM.bands_x(int256) external returns (uint256);
    function AMM.bands_y(int256) external returns (uint256);
    function AMM.set_callback(address) external; // nonpayable
    function AMM.COLLATERAL_TOKEN() external returns (address) envfree;
    function AMM.BORROWED_TOKEN() external returns (address) envfree;
    function AMM.COLLATERAL_PRECISION() external returns (uint256) envfree;
    function AMM.BORROWED_PRECISION() external returns (uint256) envfree;

    // STABLECOIN:
    function Stablecoin.balanceOf(address) external returns (uint256) envfree;
    function Stablecoin.totalSupply() external returns (uint256) envfree;

    // STABLECOIN:
    function CollateralToken.balanceOf(address) external returns (uint256) envfree;
    function CollateralToken.totalSupply() external returns (uint256) envfree;

    // WETH:

    // Factory:
    function FactoryMock.stablecoin() external returns address envfree => getStablecoin();
    function FactoryMock.admin() external returns address envfree => getFactoryAdmin();
    function FactoryMock.fee_receiver() external returns address envfree => getFeeReceiver();
    function FactoryMock.WETH() external returns address envfree => getWeth();

    // MonetaryPolicy:
    function _.rate_write() external => NONDET;
}

ghost address factoryAdmin;
ghost address feeReceiver;
ghost mathint sumAllDebt;

ghost mathint total_x { init_state axiom total_x == 0; }
ghost mathint total_y { init_state axiom total_y == 0; }

hook Sstore AMM.bands_x[KEY int256 n] uint256 newValue (uint256 oldValue) STORAGE {
    total_x = total_x - oldValue + newValue;
}

hook Sstore AMM.bands_y[KEY int256 n] uint256 newValue (uint256 oldValue) STORAGE {
    total_y = total_y - oldValue + newValue;
}

invariant liquidity_on_collateral()
    (collateraltoken.balanceOf(AMM()) - amm.admin_fees_y()) * amm.COLLATERAL_PRECISION() >= total_y;



// ghost mapping(address => uint256) loansInitialDebt {
//     init_state axiom forall address user . loansInitialDebt[user] == 0;
// }

// ghost mapping(address => uint256) loansRateMul {
//     init_state axiom forall address user . loansRateMul[user] == 0;
// }

// hook Sstore loan[KEY address user].initial_debt uint256 newInitialDebt (uint256 oldInitialDebt) STORAGE {
//     sumAllDebt = sumAllDebt - oldInitialDebt + newInitialDebt;
//     loansInitialDebt[user] = newInitialDebt;
// }

// hook Sload uint256 initialDebt loan[KEY address user].initial_debt STORAGE {
//     require  loansInitialDebt[user] == initialDebt;
// }

// hook Sstore loan[KEY address user].rate_mul uint256 newRateMul (uint256 oldRateMul) STORAGE {
//     loansRateMul[user] = newRateMul;
// }

// hook Sload uint256 newRateMul loan[KEY address user].rate_mul STORAGE {
//     require  loansRateMul[user] == newRateMul;
// }

function getFactoryAdmin() returns address {
    return factoryAdmin;
}

function getFeeReceiver() returns address {
    return feeReceiver;
}

function getStablecoin() returns address {
    return stablecoin;
}

function getWeth() returns address {
    return weth;
}

// invariant totalDebtEqSumAllDebts()
//     to_mathint(total_debt()) == sumAllDebt;


rule integrityOfCreateLoan(uint256 collateralAmaount, uint256 debt, uint256 N) {
    env e;
    mathint wethAmount = e.msg.value;
    bool loanExsitBefore = loan_exists(e.msg.sender);
    mathint mintedBefore = minted();
    mathint stablecoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);

    create_loan(e, collateralAmaount, debt, N);

    bool loanExsitAfter = loan_exists(e.msg.sender);
    uint256 initialDebt = get_initial_debt(e.msg.sender);
    mathint mintedAfter = minted();
    mathint stablecoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);

    assert !loanExsitBefore && loanExsitAfter;
    assert debt == initialDebt;
    assert mintedAfter == mintedBefore + debt;
    assert stablecoinBalanceAfter == stablecoinBalanceBefore + debt;
}

rule integrityOfRepayLoan(uint256 debtToRepay, address _for, int256 max_active_band, bool use_eth) {
    env e;
    require use_eth == false;
    mathint debtBefore = get_initial_debt(_for);
    mathint stablecoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);

    repay(e, debtToRepay, _for, max_active_band, use_eth);

    mathint debtAfter = get_initial_debt(_for);
    mathint stablecoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);

    // assert (debtBefore >= to_mathint(debtToRepay)) => debtAfter == debtBefore - debtToRepay;
    assert (debtBefore < to_mathint(debtToRepay)) => debtAfter == 0;
    // assert (debtBefore >= to_mathint(debtToRepay)) => stablecoinBalanceAfter == stablecoinBalanceBefore - debtToRepay;
    // assert (debtBefore < to_mathint(debtToRepay)) => stablecoinBalanceAfter == stablecoinBalanceBefore - debtBefore;
}

rule integrityOfAddCollateral(uint256 collateral, address _for) {
    env e;
    mathint debtBefore = get_initial_debt(_for);

    add_collateral(e, collateral, _for);

    mathint debtAfter = get_initial_debt(_for);

    assert debtBefore == debtAfter;
}

// rule integrityOfRemoveCollateral(uint256 collateral, bool use_eth) {
//     env e;

//     remove_collateral(e, collateral, use_eth);
// }

// rule integrityOfBorrowMore(uint256 collateral, uint256 debt) {
//     env e;

//     borrow_more(e, collateral, debt)

// }
