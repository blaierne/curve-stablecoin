methods {
function __init__(address, uint256, address, uint256, uint256, uint256, int256, uint256, uint256, uint256, address) external;
function approve_max(address, address) external; //approve_max(ERC20, address) internal;
function set_admin(address) external;
function sqrt_int(uint256) external returns(uint256) envfree;
function coins(uint256) external returns(address) envfree;
function limit_p_o(uint256) internal returns (uint256[2]);
function _price_oracle_ro() internal returns (uint256[2]);
function _price_oracle_w() internal returns (uint256[2]);
function price_oracle() external returns (uint256) envfree;
function dynamic_fee() external returns (uint256) envfree;
function _rate_mul() internal returns (uint256) envfree;
function get_rate_mul() external returns (uint256) envfree;
function _base_price() internal returns (uint256) envfree;
function get_base_price() external returns (uint256) envfree;
function _p_oracle_up(int256) internal returns (uint256) envfree;
function _p_current_band(int256) internal returns (uint256) envfree;

}

rule sanity(method f) {
    env e;
    calldataarg args;

    f(e, args);

    satisfy true;
}
