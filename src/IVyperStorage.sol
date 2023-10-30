// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

interface IVyperStorage {
    function store(uint256 _val) external;
    function get() external view returns (uint256);
}
