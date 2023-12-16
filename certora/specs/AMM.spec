methods {
    function total_shares(int256) external returns uint256 envfree;
    function admin() external returns address envfree;
    function BORROWED_PRECISION() external returns uint256 envfree;
    function COLLATERAL_PRECISION() external returns uint256 envfree;
    function active_band() external returns int256 envfree;
    function bands_x(int256 n) external returns uint256 envfree;
    function bands_y(int256 n) external returns uint256 envfree;
    function read_user_tick_numbers(address) external returns int256[2] envfree;
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
