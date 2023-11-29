using Stablecoin as stablecoin;
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
    function AMM.admin_fees_x() external returns (uint256);
    function AMM.admin_fees_y() external returns (uint256);
    function AMM.reset_admin_fees() external; // nonpayable
    function AMM.has_liquidity(address) external returns (bool);
    function AMM.bands_x(int256) external returns (uint256);
    function AMM.bands_y(int256) external returns (uint256);
    function AMM.set_callback(address) external; // nonpayable

    // STABLECOIN:

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

rule sanity(method f) {
    env e; 
    calldataarg args;

    f(e, args);

    assert false;
}
