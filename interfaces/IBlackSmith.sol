// SPDX-License-Identifier: AGPL-3.0

pragma solidity ^0.6.12;

interface IBlackSmith {
    function pools(address _lpToken) external view returns (uint256 weight , uint256 accRewardsPerToken , uint256 lastUpdatedAt);
    function updatePool(address _lpToken) external;

    function withdraw(address _lpToken, uint256 _amount) external;
    function deposit(address _lpToken, uint256 amount) external;

    function claimRewards(address _lpToken) external;

}