// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

interface IAMM {
    // int256 constant MAX_TICKS;               = 50
    // uint256 constant MAX_TICKS_UINT;         = 50
    // int256 constant MAX_SKIP_TICKS;          = 1024
    // ERC20 immutable BORROWED_TOKEN;          = crvUSD
    // uint256 immutable BORROWED_PRECISION;    = 1e18
    // ERC20 immutable COLLATERAL_TOKEN;        = ETH / wstETH / sfrxETH / sfrxETHv2 / wBTC / tBTC
    // uint256 immutable COLLATERAL_PRECISION;  = 1e18
    // uint256 immutable BASE_PRICE;            = 1e18

    // uint256 Aminus1;             // 99
    // uint256 A2;                  // 100 * 100
    // uint256 Aminus12;            // 99 * 99
    // uint256 SQRT_BAND_RATIO;     // sqrt(100 / 99)
    // int256 LOG_A_RATIO;          // ln(100 / 99)
    // uint256 MAX_ORACLE_DN_POW;   // (100 / 99) ** 50

    // uint256 rate_time; // timestmap
    // uint256 rate_mul = 1e18;

    // uint256 old_p_o; //
    // uint256 old_dfee; //
    // uint256 prev_p_o_time; //
    // uint256 constant PREV_P_O_DELAY; // 2 * 60  # s = 2 min
    // uint256 constant MAX_P_O_CHG; // 1.25e18 # <= 2^(1/3) - max relative change to have fee < 50%

    // mapping(int256 => uint256) total_shares;
    // mapping(address => UserTicks) user_shares;
    // uint256 constant DEAD_SHARES; // = 1000

    // --------------------------------------------------------------------------
    // GETTERS - VARIABLES
    // --------------------------------------------------------------------------
    function admin() external view returns (address); // controller
    function A() external view returns (uint256); // = 100

    function fee() external view returns (uint256);
    function admin_fee() external view returns (uint256);
    function rate() external view returns (uint256);
    function active_band() external view returns (int256);
    function min_band() external view returns (int256);
    function max_band() external view returns (int256);

    function admin_fees_x() external view returns (uint256);
    function admin_fees_y() external view returns (uint256);

    function price_oracle_contract() external view returns (address);

    function bands_x(int256 x) external view returns (uint256); // mapping(int256 => uint256) bands_x;
    function bands_y(int256 y) external view returns (uint256); // mapping(int256 => uint256) bands_y;

    function liquidity_mining_callback() external view returns (address);

    // --------------------------------------------------------------------------
    // MAIN FUNCTIONS
    // --------------------------------------------------------------------------

    // @nonreentrant('lock')
    // @only_controller
    function deposit_range(address user, uint256 amount, int256 n1, int256 n2) external;

    // @nonreentrant('lock')
    // @only_controller
    function withdraw(address user, uint256 frac) external returns (uint256[2] memory);

    //. ENTRYPOINT FOR USERS - ARB BOTS
    // @nonreentrant('lock')
    function exchange(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount, address _for /*= msg.sender*/ )
        external
        returns (uint256[2] memory);

    //. ENTRYPOINT FOR USERS - ARB BOTS
    // @nonreentrant('lock')
    function exchange_dy(uint256 i, uint256 j, uint256 out_amount, uint256 max_amount, address _for /*= msg.sender*/ )
        external
        returns (uint256[2] memory);


    // --------------------------------------------------------------------------
    // GETTERS - functions
    // --------------------------------------------------------------------------
    // 0 - gets borrowed token address
    // 1 - gets collateral token address
    function coins(uint256 i) external pure returns (address);

    // TODO
    function price_oracle() external view returns (uint256);

    // TODO
    function dynamic_fee() external view returns (uint256);

    // TODO
    function get_rate_mul() external view returns (uint256);

    // TODO
    function get_base_price() external view returns (uint256);

    // TODO
    function p_current_up(int256 n) external view returns (uint256);

    // TODO
    function p_current_down(int256 n) external view returns (uint256);

    // TODO
    function p_oracle_up(int256 n) external view returns (uint256);

    // TODO
    function p_oracle_down(int256 n) external view returns (uint256);

    // TODO
    // @nonreentrant('lock')
    function get_y_up(address user) external view returns (uint256);

    // TODO
    // @nonreentrant('lock')
    function get_x_down(address user) external view returns (uint256);

    // TODO
    // @nonreentrant('lock')
    function get_sum_xy(address user) external view returns (uint256[2] memory);

    // TODO
    // @nonreentrant('lock')
    function get_xy(address user) external view returns (uint256[50][2] memory);

    // TODO
    // @nonreentrant('lock')
    function get_amount_for_price(uint256 p) external view returns (uint256, bool);

    // TODO
    // @nonreentrant('lock')
    function get_p() external view returns (uint256);

    // TODO
    // @nonreentrant('lock')
    function read_user_tick_numbers(address user) external view returns (int256[2] memory);

    // TODO
    // @nonreentrant('lock')
    function can_skip_bands(int256 n_end) external view returns (bool);

    // TODO
    // @nonreentrant('lock')
    function active_band_with_skip() external view returns (int256);

    // TODO
    // @nonreentrant('lock')
    function has_liquidity(address user) external view returns (bool);

    // TODO
    // @nonreentrant('lock')
    function get_dy(uint256 i, uint256 j, uint256 in_amount) external view returns (uint256);

    // TODO
    // @nonreentrant('lock')
    function get_dxdy(uint256 i, uint256 j, uint256 in_amount) external view returns (uint256, uint256);

    // TODO
    // @nonreentrant('lock')
    function get_dx(uint256 i, uint256 j, uint256 out_amount) external view returns (uint256);

    // TODO
    // @nonreentrant('lock')
    function get_dydx(uint256 i, uint256 j, uint256 out_amount) external view returns (uint256, uint256);

    // --------------------------------------------------------------------------
    // GOVERNANCE ADMIN FUNCTIONS
    // --------------------------------------------------------------------------

    // function to be called once, sets controller (admin)
    function set_admin(address _admin) external;

    // @nonreentrant('lock')
    // @only_controller
    function set_rate(uint256 rate) external returns (uint256);

    // @nonreentrant('lock')
    // @only_controller
    function set_fee(uint256 fee) external;

    // @nonreentrant('lock')
    // @only_controller
    function set_admin_fee(uint256 fee) external;

    // @nonreentrant('lock')
    // @only_controller
    function reset_admin_fees() external;

    // @only_controller
    function set_callback(address liquidity_mining_callback) external;
}
