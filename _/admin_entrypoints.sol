// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

interface IControllerFactory {
// only admin functions
}

interface IStablecoin {
// ERC20 with permit
}

// MONETARY POLICIES
interface IAggMonetaryPolicy {
// only admin functions
}

interface IAggMonetaryPolicy2 {
// only admin functions
}

// PRICE ORACLES
interface IEmaPriceOracle {}

interface IAggregateStablePrice {}

interface IAggregateStablePrice2 {}

interface ICryptoWithStablePrice {}

interface ICryptoWithStablePriceAndChainlink {}

interface ICryptoWithStablePriceAndChainlinkFrxeth {}

interface ICryptoWithStablePriceETH {}

interface ICryptoWithStablePriceFrxethN {}

interface ICryptoWithStablePriceTBTC {}

interface ICryptoWithStablePriceWBTC {}

interface ICryptoWithStablePriceWstethN {}

// FACTORY
interface IFactory {
    function add_base_pool(
        address _base_pool,
        address _fee_receiver,
        uint256 _asset_type,
        address[10] memory _implementations
    ) external;

    function set_metapool_implementations(address _base_pool, address[10] memory _implementations) external;

    function set_plain_implementations(uint256 _n_coins, address[10] memory _implementations) external;

    function set_gauge_implementation(address _gauge_implementation) external;

    function set_fee_receiver(address _base_pool, address _fee_receiver) external;

    function commit_transfer_ownership(address addr) external;

    function accept_transfer_ownership() external;

    function set_manager(address _manager) external;

    function deploy_plain_pool(
        string[32] memory _name,
        string[10] memory _symbol,
        address[4] memory _coins,
        uint256 _A,
        uint256 _fee,
        uint256 _asset_type,
        uint256 _implementation_idx
    ) external returns (address);

    function deploy_gauge(address _pool) external returns (address);

    function add_token_to_whitelist(address coin, bool _add) external;
}
