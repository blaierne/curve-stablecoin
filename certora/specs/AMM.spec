methods {
//    function _.ext_p_oracle_up(int256) external => NONDET;
    function total_shares(int256) external returns uint256 envfree;
    function admin() external returns address envfree;
    function BORROWED_PRECISION() external returns uint256 envfree;
    function COLLATERAL_PRECISION() external returns uint256 envfree;
    function active_band() external returns int256 envfree;
    function bands_x(int256 n) external returns uint256 envfree;
    function bands_y(int256 n) external returns uint256 envfree;
}

ghost mapping(address => int256) user_n1;
ghost mapping(address => int256) user_n2;
ghost mapping(address => mapping(mathint => uint256)) user_ticks_unpacked {
    init_state axiom (forall address user. forall mathint n. user_ticks_unpacked[user][n] == 0);
}
ghost mapping(address => mapping(mathint => bool)) user_ticks_valid {
    init_state axiom (forall address user. forall mathint n. user_ticks_valid[user][n] == true);
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
    mathint n1 = newPacked % 2^128;
    mathint realn1;
    if (n1 >= 2^127) {
        realn1 = n1 - 2^128;
    } else {
        realn1 = n1;
    }
    mathint realn2 = (newPacked - realn1) / 2^128;
    assert realn1 < 2^128 && realn1 >= -2^127;
    assert realn2 * 2^128 + realn1 == to_mathint(newPacked);
    user_n1[user] = assert_int256(realn1);
    user_n2[user] = assert_int256(realn2);
}

hook Sload int256 packed user_shares[KEY address user].ns STORAGE {
    require user_n1[user] < 2^128 && user_n1[user] >= -2^127;
    require user_n2[user] * 2^128 + user_n1[user] == to_mathint(packed);
}

hook Sstore user_shares[KEY address user].ticks[INDEX uint256 index] uint256 newPacked (uint256 oldPacked) STORAGE {
    if (newPacked == 0 && index == 0) {
        // clear all ticks for current user
        havoc total_shares_ghost assuming
            forall mathint n. total_shares_ghost@new[n] == total_shares_ghost@old[n] - user_ticks_unpacked[user][n];
        havoc user_ticks_unpacked assuming
            forall address u. forall mathint n. user_ticks_unpacked@new[u][n] == (u == user ? 0 : user_ticks_unpacked@old[u][n]);
        havoc user_ticks_valid assuming
            forall address u. forall mathint n. !user_ticks_valid@new[u][n];
    } else {
        mathint basetick = user_n1[user] + 2 * index;
        user_ticks_valid[user][index] = true;
        total_shares_ghost[basetick + 0] = total_shares_ghost[basetick + 0] - user_ticks_unpacked[user][basetick + 0];
        total_shares_ghost[basetick + 1] = total_shares_ghost[basetick + 1] - user_ticks_unpacked[user][basetick + 1];
        user_ticks_unpacked[user][basetick + 0] = require_uint256(newPacked % 2^128);
        user_ticks_unpacked[user][basetick + 1] = require_uint256(newPacked / 2^128);
        total_shares_ghost[basetick + 0] = total_shares_ghost[basetick + 0] + user_ticks_unpacked[user][basetick + 0];
        total_shares_ghost[basetick + 1] = total_shares_ghost[basetick + 1] + user_ticks_unpacked[user][basetick + 1];
    }
}

hook Sload uint256 packed user_shares[KEY address user].ticks[INDEX uint256 index] STORAGE {
    if (user_ticks_valid[user][index]) {
        mathint basetick = user_n1[user] + 2*index;
        require to_mathint(packed) == user_ticks_unpacked[user][basetick + 0] + 2^128 * user_ticks_unpacked[user][basetick + 1];
    } else if (index == 0) {
        require to_mathint(packed) == 0;
    }
}

invariant total_shares_match(int256 n)
    total_shares_ghost[n] == to_mathint(total_shares(n))
{
    preserved {
        requireInvariant invalid_are_zero();
        requireInvariant outsiden1n2_are_zero();
    }
}

invariant zero_is_invalid()
    (forall address user. user_ticks_unpacked[user][user_n1[user]] == 0 && user_ticks_unpacked[user][user_n1[user] + 1] == 0 =>
       !user_ticks_valid[user][0]);

invariant invalid_are_zero()
    forall address user. forall mathint index.
       (!user_ticks_valid[user][0] => user_ticks_unpacked[user][index] == 0);

invariant outsiden1n2_are_zero()
    forall address user. forall mathint index.
       (index < to_mathint(user_n1[user]) || index > to_mathint(user_n2[user]) => user_ticks_unpacked[user][index] == 0)
{
    preserved {
        requireInvariant zero_is_invalid();
        requireInvariant invalid_are_zero();
    }
}

invariant low_bands_in_x(int256 n)
    n < active_band() => bands_y(n) == 0;

invariant high_bands_in_y(int256 n)
    n > active_band() => bands_x(n) == 0;

rule deposit_adds_to_bands(address user, uint256 amount, int256 n1, int256 n2) {
    env e;
    require n1 < n2;
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    deposit_range(e, user, amount, n1, n2);
    assert e.msg.sender == admin();
    assert total_x == total_x_before;
    assert total_y == total_y_before + amount * COLLATERAL_PRECISION();
}

rule withdraw_removes_from_bands(address user, uint256 frac) {
    env e;
    require BORROWED_PRECISION() != 0;
    // work around for bug in AMM.vy
    //require BORROWED_PRECISION() == 1;
    require COLLATERAL_PRECISION() != 0;
    mathint total_x_before = total_x;
    mathint total_y_before = total_y;
    uint256[2] amounts;
    amounts = withdraw(e, user, frac);
    assert e.msg.sender == admin();
    uint256 amount_x = amounts[0];
    uint256 amount_y = amounts[1];
    mathint removed_x = total_x_before - total_x;
    mathint removed_y = total_y_before - total_y;
    assert amount_x * BORROWED_PRECISION() <= removed_x && removed_x < (amount_x+2) * BORROWED_PRECISION();
    assert amount_y * COLLATERAL_PRECISION() <= removed_y && removed_y < (amount_y+2) * COLLATERAL_PRECISION();
}
