using Stablecoin as stablecoin;
using CollateralToken as collateraltoken;


methods {
    function total_shares(int256) external returns uint256 envfree;
    function admin() external returns address envfree;
    function BORROWED_PRECISION() external returns uint256 envfree;
    function COLLATERAL_PRECISION() external returns uint256 envfree;
    function active_band() external returns int256 envfree;
    function bands_x(int256 n) external returns uint256 envfree;
    function bands_y(int256 n) external returns uint256 envfree;
    function read_user_tick_numbers(address) external returns int256[2] envfree;


    // STABLECOIN:
    function Stablecoin.balanceOf(address) external returns (uint256) envfree;
    function Stablecoin.totalSupply() external returns (uint256) envfree;

    // CollateralToken:
    function CollateralToken.balanceOf(address) external returns (uint256) envfree;
    function CollateralToken.totalSupply() external returns (uint256) envfree;
}

ghost mapping(address => int256) user_ns {
    init_state axiom (forall address user. user_ns[user] == 0);
}
ghost mapping(address => mathint) user_n1 {
    init_state axiom (forall address user. user_n1[user] == 0);
}
ghost mapping(address => mathint) user_n2 {
    init_state axiom (forall address user. user_n2[user] == 0);
}
ghost mapping(address => mapping(mathint => uint256)) user_ticks_unpacked {
    init_state axiom (forall address user. forall mathint n. user_ticks_unpacked[user][n] == 0);
}
ghost mapping(address => mapping(mathint => uint256)) user_ticks_packed {
    init_state axiom (forall address user. forall mathint n. user_ticks_packed[user][n] == 0);
}
ghost mapping(mathint => mathint) total_shares_ghost {
    init_state axiom (forall mathint n. total_shares_ghost[n] == 0);
}
ghost mathint total_x { init_state axiom total_x == 0; }
ghost mathint total_y { init_state axiom total_y == 0; }

hook Sstore admin_fees_x uint256 newValue (uint256 oldValue) STORAGE {
    total_x = total_x + (newValue - oldValue) * BORROWED_PRECISION();
}

hook Sstore bands_x[KEY int256 n] uint256 newValue (uint256 oldValue) STORAGE {
    total_x = total_x - oldValue + newValue;
}

hook Sstore admin_fees_y uint256 newValue (uint256 oldValue) STORAGE {
    total_y = total_y + (newValue - oldValue) * COLLATERAL_PRECISION();
}

hook Sstore bands_y[KEY int256 n] uint256 newValue (uint256 oldValue) STORAGE {
    total_y = total_y - oldValue + newValue;
}

hook Sstore user_shares[KEY address user].ns int256 newPacked (int256 oldPacked) STORAGE {
    user_ns[user] = newPacked;

    mathint n1 = newPacked % 2^128;
    mathint realn1;
    if (n1 >= 2^127) {
        realn1 = n1 - 2^128;
    } else {
        realn1 = n1;
    }
    mathint realn2 = (newPacked - realn1 + 2^256) / 2^128 - 2^128;
    assert realn1 < 2^127 && realn1 >= -2^127;
    assert realn2 * 2^128 + realn1 == to_mathint(newPacked);
    user_n1[user] = realn1;
    user_n2[user] = realn2;
}

hook Sload int256 packed user_shares[KEY address user].ns STORAGE {
    require user_ns[user] == packed;
}

hook Sstore user_shares[KEY address user].ticks[INDEX uint256 index] uint256 newPacked (uint256 oldPacked) STORAGE {
    user_ticks_packed[user][index] = newPacked;
    if (newPacked == 0 && index == 0) {
        // clear all ticks for current user
        havoc total_shares_ghost assuming
            forall mathint n. total_shares_ghost@new[n] == total_shares_ghost@old[n] - user_ticks_unpacked[user][n];
        havoc user_ticks_unpacked assuming
            forall address u. forall mathint n. user_ticks_unpacked@new[u][n] == (u == user ? 0 : user_ticks_unpacked@old[u][n]);
    } else {
        mathint basetick = user_n1[user] + 2 * index;
        total_shares_ghost[basetick + 0] = total_shares_ghost[basetick + 0] - user_ticks_unpacked[user][basetick + 0];
        total_shares_ghost[basetick + 1] = total_shares_ghost[basetick + 1] - user_ticks_unpacked[user][basetick + 1];
        user_ticks_unpacked[user][basetick + 0] = require_uint256(newPacked % 2^128);
        user_ticks_unpacked[user][basetick + 1] = require_uint256(newPacked / 2^128);
        assert index == 0 => newPacked != 0;
        total_shares_ghost[basetick + 0] = total_shares_ghost[basetick + 0] + user_ticks_unpacked[user][basetick + 0];
        total_shares_ghost[basetick + 1] = total_shares_ghost[basetick + 1] + user_ticks_unpacked[user][basetick + 1];
    }
}

hook Sload uint256 packed user_shares[KEY address user].ticks[INDEX uint256 index] STORAGE {
    require user_ticks_packed[user][index] == packed;
}

invariant total_shares_match(int256 n)
    total_shares_ghost[n] == to_mathint(total_shares(n))
{
    preserved {
        requireInvariant unpack_invariant();
        requireInvariant n1_n2_inrange();
    }
    preserved withdraw(address user, uint256 frac) with (env e) {
        requireInvariant n1_n2_inrange();
        require to_mathint(user_ticks_unpacked[user][n]) == packed_to_unpacked(user, n);
    }
}

definition user_ticks_valid(address user) returns bool = user_ticks_packed[user][0] != 0;
definition packed_to_unpacked(address user, mathint index) returns mathint =
    (user_ticks_packed[user][0] == 0 || index < user_n1[user] || index > user_n2[user] ? 0 :
      (index - user_n1[user]) % 2 == 0 ? user_ticks_packed[user][(index - user_n1[user])/2] % 2^128
                                       : user_ticks_packed[user][(index - user_n1[user])/2] / 2^128);

invariant unpack_invariant()
    (forall address user. forall mathint index. to_mathint(user_ticks_unpacked[user][index]) == packed_to_unpacked(user, index))
{
    preserved {
        requireInvariant n1_n2_inrange();
    }
    preserved deposit_range(address user, uint256 amount, int256 n1, int256 n2) with (env e) {
        require e.msg.sender == admin() => n1 <= n2;
    }
}

invariant n1_n2_inrange()
    (forall address user. 0 <= 2^127 + user_n1[user] && user_n1[user] <= user_n2[user] && user_n2[user] < 2^127
                          && to_mathint(user_ns[user]) == user_n1[user] + 2^128 * user_n2[user])
{
    preserved deposit_range(address user, uint256 amount, int256 n1, int256 n2) with (env e) {
        require e.msg.sender == admin() => n1 <= n2;
    }
}

invariant low_bands_in_x(int256 n)
    n < active_band() => bands_y(n) == 0;

invariant high_bands_in_y(int256 n)
    n > active_band() => bands_x(n) == 0;

rule deposit_adds_to_bands(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require e.msg.sender == admin() => n1 <= n2;
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    deposit_range(e, user, amount, n1, n2);
    assert e.msg.sender == admin();
    assert total_x == total_x_before;
    assert total_y == total_y_before + amount * COLLATERAL_PRECISION();
    assert user_n1[user] == to_mathint(n1) && user_n2[user] == to_mathint(n2);
}

rule withdraw_removes_from_bands(address user, uint256 frac) {
    env e;
    requireInvariant n1_n2_inrange();
    require BORROWED_PRECISION() != 0;
    // work around for bug in AMM.vy
    require BORROWED_PRECISION() == 1;
    require COLLATERAL_PRECISION() != 0;
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    mathint num_bands = user_n2[user] - user_n1[user] + 1;
    uint256[2] amounts;
    amounts = withdraw(e, user, frac);
    assert e.msg.sender == admin();
    uint256 amount_x = amounts[0];
    uint256 amount_y = amounts[1];
    mathint removed_x = total_x_before - total_x;
    mathint removed_y = total_y_before - total_y;
    assert amount_x * BORROWED_PRECISION() <= removed_x && removed_x < (amount_x + 2 * num_bands) * BORROWED_PRECISION();
    assert amount_y * COLLATERAL_PRECISION() <= removed_y && removed_y < (amount_y + 2 * num_bands) * COLLATERAL_PRECISION();
}

rule withdraw_all_user_shares(address user) {

    env e;
    uint256[2] amounts;
    bool valid_before = user_ticks_valid(user);
    amounts = withdraw(e, user, 10^18);
    bool valid_after = user_ticks_valid(user);
    assert valid_before && !valid_after;
}

rule withdraw_some_user_shares(address user) {

    env e;
    uint256 frac;
    uint256[2] amounts;
    bool valid_before = user_ticks_valid(user);
    require frac != 10^18;
    amounts = withdraw(e, user, frac);
    bool valid_after = user_ticks_valid(user);
    assert valid_before && valid_after;
}

rule deposit_some_user_shares(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require e.msg.sender == admin() => n1 <= n2;
    bool valid_before = user_ticks_valid(user);
    deposit_range(e, user, amount, n1, n2);
    bool valid_after = user_ticks_valid(user);
    assert !valid_before && valid_after;
}

rule integrity_of_read_user_tick_numbers(address user) {
    requireInvariant n1_n2_inrange();
    env e;
    int256[2] n1n2;
    n1n2 = read_user_tick_numbers(user);
    assert n1n2[0] <= n1n2[1];
    assert to_mathint(n1n2[0]) == user_n1[user] && to_mathint(n1n2[1]) == user_n2[user];
}

rule deposit_only_in_non_active_bands(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require e.msg.sender == admin() => n1 <= n2;
    deposit_range(e, user, amount, n1, n2);
    assert n1 > active_band();
}

rule deposit_range_requires_sorted_arguments(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    deposit_range(e, user, amount, n1, n2);

    assert n1 <= n2;



    /* The deposit_range does not check whether n1 <= n2. This function is called in the following cases:
    _create_loan(mvalue: uint256, collateral: uint256, debt: uint256, N: uint256, transfer_coins: bool)
        assert N > MIN_TICKS-1, "Need more ticks" // MIN_TICKS == 4
        n1: ...
        n2: int256 = n1 + convert(N - 1, int256)

    // PASS

    _add_collateral_borrow(d_collateral: uint256, d_debt: uint256, _for: address, remove_collateral: bool):
        ns: int256[2] = self.AMM.read_user_tick_numbers(_for)
        n1: ...
        n2: int256 = n1 + unsafe_sub(ns[1], ns[0])

    repay(_d_debt: uint256, _for: address = msg.sender, max_active_band: int256 = 2**255-1, use_eth: bool = True)
        ns: int256[2] = self.AMM.read_user_tick_numbers(_for)
        if ns[0] > active_band:
            n1: ...
            n2: int256 = n1 + unsafe_sub(ns[1], ns[0])

    
    repay_extended(callbacker: address, callback_args: DynArray[uint256,5])
        ns: int256[2] = self.AMM.read_user_tick_numbers(msg.sender)
        if total_stablecoins < debt
            n1: int256 = self._calculate_debt_n1(cb.collateral, debt, size)
            n2: int256 = n1 + unsafe_sub(ns[1], ns[0])

    */
}


rule totalSharesToBandsYShouldBeConstantOnWithdraw(address user) {
    env e;
    int256 n;
    // require user_n1[user] <= to_mathint(n) && to_mathint(n) <= user_n2[user];
    require bands_y(n) > 0;
    require active_band() < n;

    uint256 frac;
    require 0 <= frac && frac <= 10^18;

    require e.msg.sender == admin();

    mathint oldRatio = (total_shares(n) * 10^18) / bands_y(n);
    require oldRatio == 10^21;
    
    withdraw(e, user, frac);
    
    require bands_y(n) > 1;

    mathint newRatio_upper = (total_shares(n) * 10^18) / (bands_y(n) - 1);
    mathint newRatio_lower = (total_shares(n) * 10^18) / (bands_y(n) + 1);
    
    assert newRatio_lower <= oldRatio;
    assert oldRatio <= newRatio_upper;
    // satisfy true;
}



rule totalSharesToBandsXShouldBeConstantOnWithdraw(address user) {
    env e;
    int256 n;
    // require user_n1[user] <= to_mathint(n) && to_mathint(n) <= user_n2[user];
    require bands_x(n) > 0;
    require active_band() < n;

    uint256 frac;
    require 0 <= frac && frac <= 10^18;

    require e.msg.sender == admin();

    mathint oldRatio = (total_shares(n) * 10^18) / bands_x(n);
    require oldRatio == 10^21;
    withdraw(e, user, frac);
    
    require bands_x(n) > 1;

    mathint newRatio_upper = (total_shares(n) * 10^18) / (bands_x(n) - 1);
    mathint newRatio_lower = (total_shares(n) * 10^18) / (bands_x(n) + 1);

    assert newRatio_lower <= oldRatio;
    assert oldRatio <= newRatio_upper;
    // satisfy true;
}

rule totalSharesToBandsYShouldBeConstantOnDepositRange(address user, uint256 amount, int256 n1, int256 n2) {
    env e;

    int256 n;

    require e.msg.sender == admin() && n1 == n2 && n == n1;
    require bands_y(n) > 0;

    mathint oldBands = bands_y(n);

    mathint oldRatio = (total_shares(n) * 10^18) / bands_y(n);

    deposit_range(e, user, amount, n1, n2);

    require bands_y(n) > 1;

    mathint newRatio_upper = (total_shares(n) * 10^18) / (bands_y(n) - 1);
    mathint newRatio_lower = (total_shares(n) * 10^18) / (bands_y(n) + 1);
    
    assert newRatio_lower <= oldRatio;
    assert oldRatio <= newRatio_upper;

    // satisfy true;
}




// Exchange... 
// i = 0, j = 1, stablecoin is going to AMM (in coin), collateral out of AMM (out coin)
// i = 1, j = 0, collateral is going to AMM, stablecoin out of AMM

// e.msg.sender sends coins, _for gets coins
rule integrityOfExchange_balance(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount, address _for) {
    env e;
    
    require (i == 0 && j == 1) || (i == 1 && j == 0);

    require _for != currentContract;
    require e.msg.sender != currentContract;

    mathint userInCoinBalanceBefore;
    mathint userOutCoinBalanceBefore;
    mathint contractInCoinBalanceBefore;
    mathint contractOutCoinBalanceBefore;

    mathint userInCoinBalanceAfter;
    mathint userOutCoinBalanceAfter;
    mathint contractInCoinBalanceAfter;
    mathint contractOutCoinBalanceAfter;
    // mathint totalXBefore = total_x * BORROWED_PRECISION();

    if (i == 0) {
        userInCoinBalanceBefore = stablecoin.balanceOf(e.msg.sender);
        contractInCoinBalanceBefore = stablecoin.balanceOf(currentContract);
        userOutCoinBalanceBefore = collateraltoken.balanceOf(_for);
        contractOutCoinBalanceBefore = collateraltoken.balanceOf(currentContract);
    } else {
        userInCoinBalanceBefore = collateraltoken.balanceOf(e.msg.sender);
        contractInCoinBalanceBefore = collateraltoken.balanceOf(currentContract);
        userOutCoinBalanceBefore = stablecoin.balanceOf(_for);
        contractOutCoinBalanceBefore = stablecoin.balanceOf(currentContract);
    }

    exchange(e, i, j, in_amount, min_amount, _for);

    if (i == 0) {
        userInCoinBalanceAfter = stablecoin.balanceOf(e.msg.sender);
        contractInCoinBalanceAfter = stablecoin.balanceOf(currentContract);
        userOutCoinBalanceAfter = collateraltoken.balanceOf(_for);
        contractOutCoinBalanceAfter = collateraltoken.balanceOf(currentContract);
    } else {
        userInCoinBalanceAfter = collateraltoken.balanceOf(e.msg.sender);
        contractInCoinBalanceAfter = collateraltoken.balanceOf(currentContract);
        userOutCoinBalanceAfter = stablecoin.balanceOf(_for);
        contractOutCoinBalanceAfter = stablecoin.balanceOf(currentContract);
    }
    

    // satisfy userOutCoinBalanceAfter > userOutCoinBalanceBefore;

    assert userInCoinBalanceBefore >= userInCoinBalanceAfter;
    assert userOutCoinBalanceBefore <= userOutCoinBalanceAfter;
    assert contractInCoinBalanceBefore <= contractInCoinBalanceAfter;
    assert contractOutCoinBalanceBefore >= contractOutCoinBalanceAfter;
    assert userInCoinBalanceBefore - userInCoinBalanceAfter == contractInCoinBalanceAfter - contractInCoinBalanceBefore;
    assert userOutCoinBalanceAfter - userOutCoinBalanceBefore == contractOutCoinBalanceBefore - contractOutCoinBalanceAfter;
}

rule exchangeDoesNotChangeUserShares(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount) {
    env e;
    require (i == 0 && j == 1) || (i == 1 && j == 0);

    address anyUser;

    mathint sharesBefore_n1 = user_n1[anyUser];
    mathint sharesBefore_n2 = user_n2[anyUser];

    exchange(e, i, j, in_amount, min_amount);

    mathint sharesAfter_n1 = user_n1[anyUser];
    mathint sharesAfter_n2 = user_n2[anyUser];

    assert sharesBefore_n1 == sharesAfter_n1;
    assert sharesBefore_n2 == sharesAfter_n2;

    // satisfy true;
}


rule integrityOfExchange_balanceMonotonicity(uint256 i, uint256 j, uint256 in_amount, uint256 min_amount) {
    env e;
    require (i == 0 && j == 1) || (i == 1 && j == 0);

    mathint borrowedTokenBalanceBefore = stablecoin.balanceOf(e.msg.sender);
    mathint totalXBefore = total_x * BORROWED_PRECISION();

    // collateraltoken.balanceOf(msg.sender);
    exchange(e, i, j, in_amount, min_amount);
    
    mathint borrowedTokenBalanceAfter = stablecoin.balanceOf(e.msg.sender);
    mathint totalXAfter = total_x * BORROWED_PRECISION();
    assert (totalXBefore < totalXAfter) => (borrowedTokenBalanceBefore <= borrowedTokenBalanceAfter);
    assert (borrowedTokenBalanceBefore < borrowedTokenBalanceAfter) => (totalXBefore <= totalXAfter);
}


/*
def exchange(i: uint256, j: uint256, in_amount: uint256, min_amount: uint256, _for: address = msg.sender) -> uint256[2]:
    """
    @notice Exchanges two coins, callable by anyone
    @param i Input coin index
    @param j Output coin index
    @param in_amount Amount of input coin to swap
    @param min_amount Minimal amount to get as output
    @param _for Address to send coins to
    @return Amount of coins given in/out
    """
    return self._exchange(i, j, in_amount, min_amount, _for, True)


@external
@nonreentrant('lock')
def exchange_dy(i: uint256, j: uint256, out_amount: uint256, max_amount: uint256, _for: address = msg.sender) -> uint256[2]:
 @notice Exchanges two coins, callable by anyone
    @param i Input coin index
    @param j Output coin index
    @param out_amount Desired amount of output coin to receive
    @param max_amount Maximum amount to spend (revert if more)
    @param _for Address to send coins to
    @return Amount of coins given in/out
    """


Borrowed token changes the same amount as total_x * precision (StableCoin)
Collateral token changes the same amount as total_y * precision

Rounding needs to be taken into account
*/
