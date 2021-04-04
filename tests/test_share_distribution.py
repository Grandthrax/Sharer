from itertools import count
from brownie import Wei, reverts
import random
import brownie


def test_share_distro(chain, interface, accounts, Contract, SharerV4):
    sms = "0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7"
    mat = "0xd9c68eb096db712FFE15ede78B3D020903F8aa30"
    ryan = "0xf1a692F2B7Da63670bf00c7376f630234Ea1bC2F"
    rando = accounts[0]
    samdev = accounts.at("0xC3D6880fD95E06C816cB030fAc45b3ffe3651Cb0", force=True)
    strategy = Contract("0x6a97FC93e39b3f792f1fD6e01565ff412B002D20")

    sharer = samdev.deploy(SharerV4)

    numOfShares = [250, 250, 500]
    contributors = [mat, ryan, sms]
    sharer.setContributors(strategy, contributors, numOfShares, {"from": rando})

    ##overwrite
    with brownie.reverts("!authorized"):
        sharer.setContributors(strategy, contributors, numOfShares, {"from": rando})

    sharer.setContributors(strategy, contributors, numOfShares, {"from": samdev})

    ##change owner
    sharer.setGovernance(rando, {"from": samdev})
    with brownie.reverts("!authorized"):
        sharer.setContributors(strategy, contributors, numOfShares, {"from": rando})

    sharer.acceptGovernance({"from": rando})
    with brownie.reverts("!authorized"):
        sharer.setContributors(strategy, contributors, numOfShares, {"from": samdev})
    sharer.setContributors(strategy, contributors, numOfShares, {"from": rando})

    sharer.setGovernance(samdev, {"from": rando})
    sharer.acceptGovernance({"from": samdev})
    sharer.setContributors(strategy, contributors, numOfShares, {"from": samdev})

    ##too many
    numOfShares = [100, 100, 100, 100]
    with brownie.reverts("length not the same"):
        sharer.setContributors(strategy, contributors, numOfShares, {"from": samdev})

    ##over 100%
    numOfShares = [500, 500, 500]
    with brownie.reverts("share total more than 100%"):
        sharer.setContributors(strategy, contributors, numOfShares, {"from": samdev})

    # Mock profit
    yshare = Contract(strategy.vault())
    treasury = accounts.at(yshare.rewards(), force=True)
    assert yshare.balanceOf(treasury) > 0
    yshare.transfer(strategy, yshare.balanceOf(treasury), {"from": treasury})
    assert yshare.balanceOf(treasury) == 0
    assert yshare.balanceOf(strategy) > 0

    # Force strategy to use Sharer rewards
    strategy.setRewards(sharer, {"from": strategy.strategist()})

    # Distributing with the list version
    sharer.distributeMultiple([strategy, strategy], {"from": samdev})
    print("==== DISTRIBUTION CALLED HERE ====")

    print("Sam bal after dis: ", yshare.balanceOf(samdev) / 1e18)
    print("Mat bal after dis: ", yshare.balanceOf(mat) / 1e18)
    print("Sharer bal after dis: ", yshare.balanceOf(sharer) / 1e18)

    assert yshare.balanceOf(ryan) > 0
    assert yshare.balanceOf(mat) > 0
    assert yshare.balanceOf(mat) == yshare.balanceOf(ryan)
    assert yshare.balanceOf(sharer) == 0
