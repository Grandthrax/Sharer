from itertools import count
from brownie import Wei, reverts
import random
import brownie

def test_share_distro(chain, interface, accounts, Contract, SharerV2):
    sms = '0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7'
    gspoosi = '0x0C703068a36D7D2199B28B67422B33Ce627B87F6'
    dmi = '0x0D77b4C6916BA6dF46dCbc4809C204dA9089FEE2'

    samdev = accounts.at('0xC3D6880fD95E06C816cB030fAc45b3ffe3651Cb0', force=True)
    rando = accounts[0]

    mat = '0xd9c68eb096db712FFE15ede78B3D020903F8aa30'
    ryan = '0xf1a692F2B7Da63670bf00c7376f630234Ea1bC2F'
    
    sharer = samdev.deploy(SharerV2)

    contributorsEx = [250, 250, 250]

    contributorA = [mat, ryan, sms]
    yshare = interface.ERC20('0x19d3364a399d251e894ac732651be8b0e4e85001')

    sharer.setContributors(yshare, contributorsEx,contributorA, {'from': rando} )

    ##overwrite
    with brownie.reverts("Only Strat MS can overwrite"):
        sharer.setContributors(yshare, contributorsEx,contributorA, {'from': rando} )

    sharer.setContributors(yshare, contributorsEx,contributorA, {'from': samdev} )

    ##too many
    contributorsEx = [100, 100, 100, 100]
    with brownie.reverts("length not the same"):
        sharer.setContributors(yshare, contributorsEx,contributorA, {'from': samdev} )

    ##over 100%
    contributorsEx = [500, 500, 500]
    with brownie.reverts("share total more than 100%"):
        sharer.setContributors(yshare, contributorsEx,contributorA, {'from': samdev} )

    print(sharer.viewContributors(yshare))
    print(sharer.viewContributors(dmi))


    yshare.transfer(sharer, yshare.balanceOf(samdev), {'from': samdev})
    print("Sam bal: ", yshare.balanceOf(samdev))
    assert yshare.balanceOf(samdev) == 0
    print("Sharer bal: ", yshare.balanceOf(sharer)/1e18)

    sharer.distribute(yshare, {'from': samdev})
    print("Sam bal after dis: ", yshare.balanceOf(samdev)/1e18)
    print("Mat bal: ", yshare.balanceOf(mat)/1e18)
    assert yshare.balanceOf(mat) == yshare.balanceOf(ryan)
    assert yshare.balanceOf(samdev) >= yshare.balanceOf(ryan)