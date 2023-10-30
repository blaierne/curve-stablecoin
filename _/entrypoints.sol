// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

// USER ENTRYPOINTS

// 0/2
interface IAMM {
    // @nonreentrant('lock')
    function exchange(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount, address _for /* = msg.sender */ )
        external
        returns (uint256[2] memory);

    // @nonreentrant('lock')
    function exchange_dy(uint256 i, uint256 j, uint256 out_amount, uint256 max_amount, address _for /* = msg.sender */ )
        external
        returns (uint256[2] memory);
}

// 0/10
interface IController {
    // @nonreentrant('lock')
    function create_loan(uint256 collateral, uint256 debt, uint256 N) external payable;

    // @nonreentrant('lock')
    function create_loan_extended(
        uint256 collateral,
        uint256 debt,
        uint256 N,
        address callbacker,
        uint256[][5] memory callback_args
    ) external payable;

    // @nonreentrant('lock')
    function add_collateral(uint256 collateral, address _for /* = msg.sender */ ) external payable;

    // @nonreentrant('lock')
    function remove_collateral(uint256 collateral, bool use_eth /* = True */ ) external;

    // @nonreentrant('lock')
    function borrow_more(uint256 collateral, uint256 debt) external payable;

    // @nonreentrant('lock')
    function repay(
        uint256 _d_debt,
        address _for, /* = msg.sender */
        int256 max_active_band, /* = 2**255-1 */
        bool use_eth /* = True */
    ) external;

    // @nonreentrant('lock')
    function repay_extended(address callbacker, uint256[][5] memory callback_args) external;

    // @nonreentrant('lock')
    function liquidate(address user, uint256 min_x, bool use_eth /* = True */ ) external;

    // @nonreentrant('lock')
    function liquidate_extended(
        address user,
        uint256 min_x,
        uint256 frac,
        bool use_eth,
        address callbacker,
        uint256[][5] memory callback_args
    ) external;

    // @nonreentrant('lock')
    function collect_fees() external returns (uint256);
}

interface IStablecoin {
// ERC20 with permit
}

// STABILIZER
// 0/2
interface IPegKeeper {
    function update(address _beneficiary /* = msg.sender */ ) external returns (uint256);

    function withdraw_profit() external returns (uint256);
}

// PRICE ORACLES
// all oracles have external `price_w()` function

// 0/1
interface IEmaPriceOracle {
    function price_w() external returns (uint256);
}

interface IAggregateStablePrice {}

interface IAggregateStablePrice2 {}

interface ICryptoWithStablePrice {}

interface ICryptoWithStablePriceAndChainlink {}

interface ICryptoWithStablePriceAndChainlinkFrxeth {}

interface ICryptoWithStablePriceETH {
    function price_w() external returns (uint256);
}

interface ICryptoWithStablePriceFrxethN {}

interface ICryptoWithStablePriceTBTC {}

interface ICryptoWithStablePriceWBTC {}

interface ICryptoWithStablePriceWstethN {}