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
    // function def create_loan_extended(uint256, uint256, uint256, address, DynArray[uint256,5]) external; // payable nonreentrant
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
}

rule sanity(method f) {
    env e; 
    calldataarg args;

    f(e, args);

    assert false;
}
