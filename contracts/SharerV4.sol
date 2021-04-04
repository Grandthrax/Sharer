pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

interface IStrategy {
    function vault() external view returns (address);
}

//for version 0.3.1 or above of base strategy

contract SharerV4 {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    event ContributorsSet(
        address indexed strategy,
        address[] contributors,
        uint256[] numOfShares
    );
    event Distribute(address indexed strategy, uint256 totalDistributed);

    struct Contributor {
        address contributor;
        uint256 numOfShares;
    }
    mapping(address => Contributor[]) public shares;
    address public governance;
    address public pendingGovernance;

    constructor() public {
        governance = msg.sender;
    }

    function setGovernance(address _governance) external {
        require(msg.sender == governance);
        pendingGovernance = _governance;
    }

    function acceptGovernance() external {
        require(msg.sender == pendingGovernance);
        governance = pendingGovernance;
    }

    function viewContributors(address strategy)
        public
        view
        returns (Contributor[] memory)
    {
        return shares[strategy];
    }

    // Contributors for a strategy are set all at once, not on individual basis.
    // Initialization of contributors list for any strategy can be done by anyone. Afterwards, only Strategist MS can call this
    // If sum of total shares set < 1,000, any remainder of shares will go to strategist multisig
    function setContributors(
        address strategy,
        address[] calldata _contributors,
        uint256[] calldata _numOfShares
    ) public {
        require(
            _contributors.length == _numOfShares.length,
            "length not the same"
        );
        require(
            shares[strategy].length == 0 || msg.sender == governance,
            "!authorized"
        );

        delete shares[strategy];
        uint256 totalShares = 0;

        for (uint256 i = 0; i < _contributors.length; i++) {
            totalShares = totalShares.add(_numOfShares[i]);
            shares[strategy].push(
                Contributor(_contributors[i], _numOfShares[i])
            );
        }

        require(totalShares <= 1000, "share total more than 100%");
        emit ContributorsSet(strategy, _contributors, _numOfShares);
    }

    function distributeMultiple(address[] calldata _strategies) public {
        for (uint256 i = 0; i < _strategies.length; i++) {
            distribute(_strategies[i]);
        }
    }

    function distribute(address _strategy) public {
        IStrategy strategy = IStrategy(_strategy);
        IERC20 reward = IERC20(strategy.vault());

        uint256 totalRewards = reward.balanceOf(_strategy);
        if (totalRewards <= 1000) {
            return;
        }
        uint256 remainingRewards = totalRewards;
        Contributor[] memory contributorsT = shares[_strategy];

        // Distribute rewards to everyone but the last person
        for (uint256 i = 0; i < contributorsT.length - 1; i++) {
            address cont = contributorsT[i].contributor;
            uint256 share =
                totalRewards.mul(contributorsT[i].numOfShares).div(1000);
            reward.safeTransferFrom(_strategy, cont, share);
            remainingRewards -= share;
        }

        // Last person takes the reminder
        address _last = contributorsT[contributorsT.length - 1].contributor;
        reward.safeTransferFrom(_strategy, _last, remainingRewards);

        emit Distribute(_strategy, totalRewards);
    }

    function checkBalance(address _strategy) public view returns (uint256) {
        IStrategy strategy = IStrategy(_strategy);
        IERC20 reward = IERC20(strategy.vault());
        return reward.balanceOf(_strategy);
    }
}
