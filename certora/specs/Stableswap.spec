methods {
    // ERC20 functionality
    function _transfer(address, address, uint256) internal;
    function transfer(address, uint256) external returns (bool);
    function transferFrom(address, address, uint256) external returns (bool);
    function approve(address, uint256) external returns (bool);
    function permit(address, address, uint256, uint256, uint8, bytes32, bytes32) external returns (bool);

    // Getters: 
    function allowance(address, address) external returns (uint256) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;

    // Stableswap functionality
    function last_price() external returns(uint256) envfree;
    function ema_price() external returns(uint256) envfree;
    function get_balances() external returns(uint256[2]) envfree;
    function admin_fee() external returns(uint256) envfree;
    function A() external returns(uint256);
    function A_precise() external returns(uint256);
    function get_p() external returns(uint256);
    function price_oracle() external returns(uint256);
    function get_virtual_price() external returns(uint256);
    function calc_token_amount(uint256[], bool) external returns(uint256);
    function add_liquidity(uint256[], uint256, address) external returns(uint256);
    function remove_liquidity(uint256, uint256[], address) external returns(uint256[]);
    function remove_liquidity_imbalance(uint256[], uint256, address) external returns(uint256[]);
    function get_dy(int128, int128, uint256) external returns(uint256) envfree;
    function get_dx(int128, int128, uint256) external returns(uint256) envfree;
    function exchange(int128, int128, uint256, uint256, address) external returns(uint256);
    function calc_withdraw_one_coin(uint256, int128) external returns(uint256);
    function ramp_A(uint256, uint256) external;
    function stop_ramp_A() external;
    function set_ma_exp_time(uint256) external;
    function admin_balances(uint256) external returns(uint256);
    function commit_new_fee(uint256) external;
    function apply_new_fee() external;
    function withdraw_admin_fees() external;




	// // Constants
	// function N_COINS() external returns uint256 envfree;
	// function N_COINS_128() external returns int128 envfree;
	// function PRECISION() external returns uint256 envfree;
	// function FEE_DENOMINATOR() external returns uint256 envfree;
	// function ADMIN_FEE() external returns uint256 envfree;
	// function A_PRECISION() external returns uint256 envfree;
	// function MAX_FEE() external returns uint256 envfree;
	// function MAX_A() external returns uint256 envfree;
}

// function setConstants(env e) {
// 	require N_COINS() == 2;
// 	require N_COINS_128() == 2;
// 	require PRECISION() == 10^18;
// 	require FEE_DENOMINATOR() == 10^10;
// 	require ADMIN_FEE() == 5000000000;
// 	require A_PRECISION() == 100;
//     require MAX_FEE() == 5*10^9;
// 	require MAX_A() == 1000000;
// }


//////////////////////////////////////////
/////// Approve does not revert when e.msg.sender 
//////////////////////////////////////////




/* 
	Property: Find and show a path for each method.
*/
rule reachability(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	satisfy true;
}



/* 
   	Property: Define and check functions that should never revert
	Notice:  use f.selector to state which functions should not revert,e.g.f.selector == sig:balanceOf(address).selector 
*/  
definition nonReveritngFunction(method f ) returns bool = 
    f.selector == sig:balanceOf(address).selector ||
    f.selector == sig:allowance(address, address).selector ||
    f.selector == sig:totalSupply().selector; 

definition canIncreaseAllowance(method f ) returns bool = 
	f.selector == sig:approve(address,uint256).selector || 
	f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector;

definition canDecreaseAllowance(method f ) returns bool = 
	f.selector == sig:approve(address,uint256).selector || 
	f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector;

definition canIncreaseBalance(method f ) returns bool = 
	f.selector == sig:transfer(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256).selector;

definition canDecreaseBalance(method f ) returns bool = 
	f.selector == sig:transfer(address,uint256).selector ||
	f.selector == sig:transferFrom(address,address,uint256).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector;

definition priveledgedFunction(method f ) returns bool = false;

definition canIncreaseTotalSupply(method f ) returns bool = 
    f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256).selector;

definition canDecreaseTotalSupply(method f ) returns bool = 
    f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector;

/*
	List of functions we assume are allowd to change the [totalSupply]
*/

definition canChangeTotalSupply(method f ) returns bool = 
    f.selector == sig:add_liquidity(uint256[2], uint256, address).selector ||
    f.selector == sig:add_liquidity(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2], address).selector ||
    f.selector == sig:remove_liquidity(uint256, uint256[2]).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256, address).selector ||
    f.selector == sig:remove_liquidity_imbalance(uint256[2], uint256).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256,address).selector ||
    f.selector == sig:remove_liquidity_one_coin(uint256,int128,uint256).selector;


rule transferFromChangesBalanceAndAllowanceCorrectly() {
	env e;
	address spender = e.msg.sender;
	address owner;
	address recipient;

	uint256 allowedBefore = allowance(owner, spender);
    require allowedBefore < max_uint256; // Max value behaves like infinity in the Stableswap.
	uint256 ownerBalanceBefore = balanceOf(owner);
	uint256 recipientBalanceBefore = balanceOf(recipient);
	uint256 transfered;

	transferFrom(e, owner, recipient, transfered);

	assert allowedBefore == assert_uint256(allowance(owner, spender) + transfered);

	if(owner == recipient) {
		assert assert_uint256(ownerBalanceBefore) == balanceOf(owner);
	} else { 
		assert assert_uint256(ownerBalanceBefore - transfered) == balanceOf(owner);
		assert assert_uint256(recipientBalanceBefore + transfered) == balanceOf(recipient);
	}
}


rule transferFromRevertingConditions() {
    address owner;
	env e;
	require e.msg.value == 0;
	address spender = e.msg.sender;
	address recipient;

	uint256 allowed = allowance(owner, spender);
	uint256 transfered;

    // bool zeroAddress = owner == 0 || recipient == 0 || e.msg.sender == 0;
    bool zeroAddress = recipient == 0;
    bool allowanceIsLow = allowed < transfered;
    bool notEnoughBalance = balanceOf(owner) < transfered;
    bool overflow = recipient != owner && balanceOf(recipient) + transfered > max_uint;

    bool shouldRevert = zeroAddress || allowanceIsLow || notEnoughBalance || overflow;

    transferFrom@withrevert(e, owner, recipient, transfered);   
	assert lastReverted <=> shouldRevert;	
}

rule approveSetsAllowance() {
	env e;
	address spender;
	address owner = e.msg.sender;
	uint amount;

	approve(e, spender, amount);
	uint256 allowed = allowance(owner, spender);
	assert allowed == amount;
}

rule approveRevertingConditions() {
    env e;
	require e.msg.value == 0;
	address spender;
	address owner = e.msg.sender;
	uint amount;

    // Does not revert for owner == 0 nor spender == 0
	// bool zeroAddress = owner == 0 || spender == 0;
	// bool shouldRevert = zeroAddress;
    bool shouldRevert = false;
    
	approve@withrevert(e, spender, amount);
	assert lastReverted == shouldRevert;
}

rule transferChangesBalanceCorrectly() {
	env e;
    address recipient;
    uint256 amount;

    mathint balanceOfRecipientBefore = balanceOf(recipient);
    mathint balanceOfSenderBefore = balanceOf(e.msg.sender);

    transfer(e, recipient, amount);

	if(e.msg.sender != recipient) {
		assert balanceOf(e, recipient) == assert_uint256(balanceOfRecipientBefore + amount);
		assert balanceOf(e, e.msg.sender) == assert_uint256(balanceOfSenderBefore - amount);
	} else {
		assert balanceOf(e, e.msg.sender) == assert_uint256(balanceOfSenderBefore);
	}
}

rule transferRevertingConditions {
	env e;
	address recipient;
	uint256 amount;
    require e.msg.value == 0;

	bool senderBalanceTooLow = balanceOf(e.msg.sender) < amount;
    // bool zeroRecipient = recipient == 0;
    bool zeroSender = e.msg.sender == 0;
    bool senderIsRecipient = e.msg.sender == recipient;

    bool recipientBalanceOverflows = balanceOf(recipient) + amount > max_uint256 && !senderIsRecipient;

    // bool shouldRevert = senderBalanceTooLow || zeroRecipient || zeroSender || recipientBalanceOverflows;
    bool shouldRevert = senderBalanceTooLow || recipientBalanceOverflows;

	transfer@withrevert(e, recipient, amount);
	assert lastReverted <=> shouldRevert;
}



//
// In the following part, we check for every variable (e.g. balances or allowance) that:
// 1. they can be changed only by privileged methods, and
// 2. the privileged methods might change variables corresponding only to the users 
// 	that call the methods
//


/*
	Functions that are not not allowed to change the [totalSupply] (via [canChangeTotalSupply()])
	do not change the total balance.
*/
rule totalSuppyDoesNotChange(method f) filtered {f -> !canChangeTotalSupply(f) } 
{		
	env e;
	calldataarg args;

	uint256 before = totalSupply(e);
	f(e,args);
    uint256 after = totalSupply(e);
	assert before == after;
}


/*
	The below function just calls (dispatch) all methods (an arbitrary one) from the contract, 
	using given [env e], [address from] and [address to].
	We use this function in several rules, including: . The usecase is typically to show that 
	the call of the function does not affect a "property" of a third party (i.e. != e.msg.sender, from, to),
	such as the balance or allowance.  

*/
function callFunctionWithParams(env e, method f, address from, address to) {
	uint256 amount;

	if (f.selector == sig:transfer(address, uint256).selector) {
		require from == e.msg.sender;
		transfer(e, to, amount);
	} else if (f.selector == sig:allowance(address, address).selector) {
		allowance(e, from, to);
	} else if (f.selector == sig:approve(address, uint256).selector) {
		approve(e, to, amount);
	} else if (f.selector == sig:transferFrom(address, address, uint256).selector) {
		transferFrom(e, from, to, amount);
	} else if (f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector) {
        uint256 deadline; uint8 _v; bytes32 _r; bytes32 _s;
        permit(e, from, to, amount, deadline, _v, _r, _s);
    } else {
		calldataarg args;
		f(e, args);
	}
}

/*
	Given addresses [e.msg.sender], [from], [to] and [thirdParty], we check that 
	there is no method [f] that would:
	1] not take [thirdParty] as an input argument, and
	2] yet changed the balance of [thirdParty].
	Intuitively, we target e.g. the case where a transfer of tokens [from] -> [to]
	changes the balance of [thirdParty]. 
*/
rule doesNotAffectAThirdPartyBalance(method f) {
	env e;	
	address from;
	address to;
	address thirdParty;

	require (thirdParty != from) && (thirdParty != to) && (thirdParty != e.msg.sender);

	uint256 thirdBalanceBefore = balanceOf(e, thirdParty);
	callFunctionWithParams(e, f, from, to);

	assert balanceOf(e, thirdParty) == thirdBalanceBefore;
}

/*
	Given addresses [e.msg.sender], [from], [to] and [thirdParty], we check that 
	there is no method [f] that would:
	1] not take [thirdParty] as an input argument, and
	2] yet changed the allowance of [thirdParty] w.r.t a [thirdPartySpender].
*/
rule doesNotAffectAThirdPartyAllowance(method f) {
	env e;	
	address from;
	address to;
	address thirdParty;
	address thirdPartySpender;

	require (thirdParty != from) && (thirdParty != to) && (thirdParty != e.msg.sender);

	uint256 spenderAllowanceBefore = allowance(e, thirdParty, thirdPartySpender);
	callFunctionWithParams(e, f, from, to);
    require f.selector != sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector;

	assert allowance(e, thirdParty, thirdPartySpender) == spenderAllowanceBefore;
}


rule onlyAllowedMethodsMayChangeBalance(method f) {
	env e;
	address addr;
	uint256 balanceBefore = balanceOf(addr);
	calldataarg args;
	f(e,args);
	uint256 balanceAfter = balanceOf(addr);
	assert balanceAfter > balanceBefore => canIncreaseBalance(f), "should not increase balance";
	assert balanceAfter < balanceBefore => canDecreaseBalance(f), "should not decrease balance";
}

/*
	Checks that functions that can change the balance change balance only of the relevant adresses, 
	i.e, do not affect a third party. For example, burn(...) should decrease a balance only of a single address.
*/
rule whoCanChangeBalance(method f) filtered {f -> canDecreaseBalance(f) || canIncreaseBalance(f) } {
	env e;
	address mightChange;
	address shouldNotChange;
	require mightChange != shouldNotChange;
	uint256 balanceBefore = balanceOf(shouldNotChange);
	
	uint256 amount;
	address receiver;
	require receiver != shouldNotChange;

	if (f.selector == sig:transfer(address,uint256).selector) {
		require e.msg.sender == mightChange;
		transfer(e, receiver, amount);
	} else if(f.selector == sig:transferFrom(address,address,uint256).selector) {
		transferFrom(e, mightChange, receiver, amount);
	} else {
		// This is here to trigger when user adds a new function to the smart contract that
		// can change the balance. In such case, we should include corresponding [else if] here.
		assert false;
	}

	assert balanceBefore == balanceOf(shouldNotChange);
}

rule onlyAllowedMethodsMayChangeAllowance(method f) {
	env e;
	address addr1;
	address addr2;
	uint256 allowanceBefore = allowance(addr1, addr2);
	calldataarg args;
	f(e,args);
    require f.selector != sig:add_liquidity(uint256[2],uint256,address).selector;
	uint256 allowanceAfter = allowance(addr1, addr2);
	assert allowanceAfter > allowanceBefore => canIncreaseAllowance(f), "should not increase allowance";
	assert allowanceAfter < allowanceBefore => canDecreaseAllowance(f), "should not decrease allowance";
}

/*
	Checks that functions that can change the balance change balance only of the relevant adresses, 
	i.e, do not affect a third party. For example, burn(...) should decrease a balance only of a single address.
*/
rule whoCanChangeAllowance(method f) filtered { f -> canDecreaseAllowance(f) || canIncreaseAllowance(f) } {
	env e;
	address owner;
	address spender;
	uint256 amountToChange;	

	address otherOwner;
	address otherSpender;
	uint256 theOtherAllowance = allowance(otherOwner, otherSpender);
    
    require f.selector != sig:permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector; // this function is a bit tricky

	if(f.selector == sig:approve(address,uint256).selector) {		
		require owner == e.msg.sender;
		uint256 newAllowance;
		require to_mathint(amountToChange) == allowance(owner, spender) - newAllowance;
		approve(e, spender, newAllowance);
	} else if(f.selector == sig:transferFrom(address,address,uint256).selector) {
		address recipient;
		require e.msg.sender == spender;
		transferFrom(e, owner, recipient, amountToChange);
	} else {
		// This is here to trigger when user adds a new function to the smart contract that
		// can change the balance. In such case, we should include corresponding [else if] here.
		assert false;
	}

	uint256 newAllowanceOfTheOther = allowance(otherOwner, otherSpender);

	assert theOtherAllowance != newAllowanceOfTheOther <=>
		(otherSpender == spender && otherOwner == owner && amountToChange > 0 && theOtherAllowance < max_uint256);
}

rule onlyAllowedMethodsMayChangeTotalSupply(method f) {
	env e;
	uint256 totalSupplyBefore = totalSupply();
	calldataarg args;
	f(e,args);
	uint256 totalSupplyAfter = totalSupply();
	assert totalSupplyAfter > totalSupplyBefore => canIncreaseTotalSupply(f), "should not increase total supply";
	assert totalSupplyAfter < totalSupplyBefore => canDecreaseTotalSupply(f), "should not decrease total supply";
}




// Invertiblity of get_dx and get_dy
/*
def get_dy(i: int128, j: int128, dx: uint256) -> uint256:
    """
    @notice Calculate the current output dy given input dx
    @dev Index values can be found via the `coins` public getter method
    @param i Index value for the coin to send
    @param j Index valie of the coin to recieve
    @param dx Amount of `i` being exchanged
    @return Amount of `j` predicted
	"""	

// Send dx of coin i, returns the number of coins j received.


def get_dx(i: int128, j: int128, dy: uint256) -> uint256:
    """
    @notice Calculate the current input dx given output dy
    @dev Index values can be found via the `coins` public getter method
    @param i Index value for the coin to send
    @param j Index valie of the coin to recieve
    @param dy Amount of `j` being received after exchange
    @return Amount of `i` predicted
    """
*/

// Want to get dy of coin j, returns how much should I send of i to get it.

rule invertibilityOfget_dxAndget_dy(env e, int128 i, int128 j, uint256 dx) {
	require i == 0 || i == 1;
	require j == 0 || j == 1;
	require i != j;

	uint256 dy = get_dy(i, j, dx); // I send dx of coin i and get dy of coin j.
	uint256 new_dx = get_dx(i, j, dy); // I want to receive dy of coin j, I need to send new_dx of coint i.

	// dx and new_dx should match - both lead to getting dy of coin j.
	assert dx == new_dx;
}

rule invertibilityOfget_dxAndget_dyNeq1(env e, int128 i, int128 j, uint256 dx) {
	require i == 0 || i == 1;
	require j == 0 || j == 1;
	require i != j;
	uint256 dy = get_dy(i, j, dx); // I send dx of coin i and get dy of coin j.
	uint256 new_dx = get_dx(i, j, dy); // I want to receive dy of coin j, I need to send new_dx of coint i.

	// dx and new_dx should match - both lead to getting dy of coin j.
	assert dx >= new_dx;
}

rule invertibilityOfget_dxAndget_dyNeq2(env e, int128 i, int128 j, uint256 dx) {
	require i == 0 || i == 1;
	require j == 0 || j == 1;
	require i != j;
	uint256 dy = get_dy(i, j, dx); // I send dx of coin i and get dy of coin j.
	uint256 new_dx = get_dx(i, j, dy); // I want to receive dy of coin j, I need to send new_dx of coint i.

	// dx and new_dx should match - both lead to getting dy of coin j.
	assert dx <= new_dx;
}

rule invertibilityOfget_dyAndget_dx(env e, int128 i, int128 j, uint256 dy) {
	require i == 0 || i == 1;
	require j == 0 || j == 1;
	require i != j;
	uint256 dx = get_dx(i, j, dy);
	uint256 new_dy = get_dy(i, j, dx);

	// dy and new_dy should match - both express how much I get for selling dy of coin j.
	assert dy == new_dy;
}

rule invertibilityOfget_dyAndget_dxNeq1(env e, int128 i, int128 j, uint256 dy) {
	require i == 0 || i == 1;
	require j == 0 || j == 1;
	require i != j;
	uint256 dx = get_dx(i, j, dy);
	uint256 new_dy = get_dy(i, j, dx);

	// dy and new_dy should match - both express how much I get for selling dy of coin j.
	assert dy >= new_dy;
}

rule invertibilityOfget_dyAndget_dxNeq2(env e, int128 i, int128 j, uint256 dy) {
	require i == 0 || i == 1;
	require j == 0 || j == 1;
	require i != j;
	uint256 dx = get_dx(i, j, dy);
	uint256 new_dy = get_dy(i, j, dx);

	// dy and new_dy should match - both express how much I get for selling dy of coin j.
	assert dy <= new_dy;
}

// Function get_dx should predict the result of exchange




// Functions get_D, get_y do not revert


























// ghost mathint sum_of_balances {
//     init_state axiom sum_of_balances == 0;
// }

// hook Sstore balanceOf[KEY address user] uint256 newvalue (uint256 oldvalue) STORAGE {
//     sum_of_balances = sum_of_balances + newvalue - oldvalue;
// }

// invariant totalSupplyEqualsSum()
//     to_mathint(totalSupply()) == sum_of_balances;

// /*
//     @Description:
//         Balance of address 0 is always 0
// */
// invariant ZeroAddressNoBalance()
//     balanceOf(0) == 0;

// function doesntChangeBalance(method f) returns bool {
//     return f.selector != sig:transfer(address,uint256).selector &&
//         f.selector != sig:transferFrom(address,address,uint256).selector;
// }

// /*
//     @Description:
//         Verify that there is no fee on transfer() (like potentially on USDT)
// */
// rule noFeeOnTransfer(address bob, uint256 amount) {
//     env e;
//     require bob != e.msg.sender;
//     mathint balanceSenderBefore = balanceOf(e.msg.sender);
//     mathint balanceBefore = balanceOf(bob);

//     bool sucsess = transfer(e, bob, amount);

//     mathint balanceAfter = balanceOf(bob);
//     mathint balanceSenderAfter = balanceOf(e.msg.sender);
//     assert balanceAfter == balanceBefore + amount;
//     assert balanceSenderAfter == balanceSenderBefore - amount;
// }

// /*
//     @Description:
//         Verify that there is no fee on transferFrom() (like potentially on USDT)
// */
// rule noFeeOnTransferFrom(address alice, address bob, uint256 amount) {
//     env e;
//     require alice != bob;
//     mathint balanceBefore = balanceOf(bob);
//     mathint balanceAliceBefore = balanceOf(alice);

//     bool sucsess = transferFrom(e, alice, bob, amount);

//     mathint balanceAfter = balanceOf(bob);
//     mathint balanceAliceAfter = balanceOf(alice);
//     assert sucsess => balanceAfter == balanceBefore + amount;
//     assert sucsess => balanceAliceAfter == balanceAliceBefore - amount;
//     assert !sucsess => balanceAfter == balanceBefore;
//     assert !sucsess => balanceAliceAfter == balanceAliceBefore;
// }

// /*
//     @Description:
//         Token transfer works correctly. Balances are updated if not reverted. 
//         If reverted then the transfer amount was too high, or the recipient is 0.

//     @Notes:
//         This rule fails on tokens with a blacklist function, like USDC and USDT.
//         The prover finds a counterexample of a reverted transfer to a blacklisted address or a transfer in a paused state.
// */
// rule transferCorrect(address to, uint256 amount) {
//     env e;
//     require e.msg.value == 0 && e.msg.sender != 0;
//     mathint fromBalanceBefore = balanceOf(e.msg.sender);
//     mathint toBalanceBefore = balanceOf(to);
//     require fromBalanceBefore + toBalanceBefore <= max_uint256;

//     bool sucsess = transfer@withrevert(e, to, amount);
//     bool reverted = lastReverted;
//     if (!reverted) {
//         if (e.msg.sender == to) {
//             assert to_mathint(balanceOf(e.msg.sender)) == fromBalanceBefore;
//         } else {
//             assert to_mathint(balanceOf(e.msg.sender)) == fromBalanceBefore - amount;
//             assert to_mathint(balanceOf(to)) == toBalanceBefore + amount;
//         }
//     } else {
//         assert to_mathint(amount) > fromBalanceBefore || to == 0 || to == currentContract;
//     }
// }

// /*
//     @Description:
//         Test that transferFrom works correctly. Balances are updated if not reverted. 
//         If reverted, it means the transfer amount was too high, or the recipient is 0

//     @Notes:
//         This rule fails on tokens with a blacklist and or pause function, like USDC and USDT.
//         The prover finds a counterexample of a reverted transfer to a blacklisted address or a transfer in a paused state.
// */

// rule transferFromCorrect(address from, address to, uint256 amount) {
//     env e;
//     require e.msg.value == 0;
//     mathint fromBalanceBefore = balanceOf(from);
//     mathint toBalanceBefore = balanceOf(to);
//     mathint allowanceBefore = allowance(from, e.msg.sender);
//     require fromBalanceBefore + toBalanceBefore <= max_uint256;

//     bool sucsess = transferFrom(e, from, to, amount);

//     mathint fromBalanceAfter = balanceOf(from);
//     mathint toBalanceAfter = balanceOf(to);
//     mathint allowanceAfter = allowance(from, e.msg.sender);

//     assert from != to =>
//         fromBalanceAfter == fromBalanceBefore - amount &&
//         toBalanceAfter == toBalanceBefore + amount;
//     assert from != to && allowanceBefore != max_uint256 =>
//         allowanceAfter == allowanceBefore - amount;
// }

// /*
//     @Description:
//         transferFrom should revert if and only if the amount is too high or the recipient is 0.

//     @Notes:
//         Fails on tokens with pause/blacklist functions, like USDC.
// */
// rule transferFromReverts(address from, address to, uint256 amount) {
//     env e;
//     uint256 allowanceBefore = allowance(from, e.msg.sender);
//     uint256 fromBalanceBefore = balanceOf(from);
//     require from != 0 && e.msg.sender != 0;
//     require e.msg.value == 0;
//     require fromBalanceBefore + balanceOf(to) <= max_uint256;

//     transferFrom@withrevert(e, from, to, amount);

//     assert lastReverted <=> (allowanceBefore < amount || amount > fromBalanceBefore || to == 0 || to == currentContract);
// }

// /*
//     @Description:
//         Transfer from msg.sender to alice doesn't change the balance of other addresses
// */
// rule TransferDoesntChangeOtherBalance(address to, uint256 amount, address other) {
//     env e;
//     require other != e.msg.sender;
//     require other != to && other != currentContract;
//     uint256 balanceBefore = balanceOf(other);
//     transfer(e, to, amount); 
//     assert balanceBefore == balanceOf(other);
// }

// /*
//     @Description:
//         Transfer from alice to bob using transferFrom doesn't change the balance of other addresses
// */
// rule TransferFromDoesntChangeOtherBalance(address from, address to, uint256 amount, address other) {
//     env e;
//     require other != from;
//     require other != to;
//     uint256 balanceBefore = balanceOf(other);
//     transferFrom(e, from, to, amount); 
//     assert balanceBefore == balanceOf(other);
// }

// /*  
//     @Description:
//         Allowance changes correctly as a result of calls to approve, transfer, increaseAllowance, decreaseAllowance

//     @Notes:
//         Some ERC20 tokens have functions like permit() that change allowance via a signature. 
//         The rule will fail on such functions.
// */
// /*
// rule ChangingAllowance(method f, address from, address spender) {
//     uint256 allowanceBefore = allowance(from, spender);
//     env e;
//     if (f.selector == sig:approve(address, uint256).selector) {
//         address spender_;
//         uint256 amount;
//         approve(e, spender_, amount);
//         if (from == e.msg.sender && spender == spender_) {
//             assert allowance(from, spender) == amount;
//         } else {
//             assert allowance(from, spender) == allowanceBefore;
//         }
//     } else if (f.selector == sig:transferFrom(address,address,uint256).selector) {
//         address from_;
//         address to;
//         uint256 amount;
//         transferFrom(e, from_, to, amount);
//         mathint allowanceAfter = allowance(from, spender);
//         if (from == from_ && spender == e.msg.sender) {
//             assert from == to || allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
//         } else {
//             assert allowance(from, spender) == allowanceBefore;
//         }
//     } else if (f.selector == sig:decreaseAllowance(address, uint256).selector) {
//         address spender_;
//         uint256 amount;
//         require amount <= allowanceBefore;
//         decreaseAllowance(e, spender_, amount);
//         if (from == e.msg.sender && spender == spender_) {
//             assert to_mathint(allowance(from, spender)) == allowanceBefore - amount;
//         } else {
//             assert allowance(from, spender) == allowanceBefore;
//         }
//     } else if (f.selector == sig:increaseAllowance(address, uint256).selector) {
//         address spender_;
//         uint256 amount;
//         require amount + allowanceBefore < max_uint256;
//         increaseAllowance(e, spender_, amount);
//         if (from == e.msg.sender && spender == spender_) {
//             assert to_mathint(allowance(from, spender)) == allowanceBefore + amount;
//         } else {
//             assert allowance(from, spender) == allowanceBefore;
//         }
//     } else if (f.selector == sig:burnFrom(address, uint256).selector) {
//         address from_;
//         uint256 amount;
//         burnFrom(e, from_, amount);
//         mathint allowanceAfter = allowance(from, spender);
//         if (from == from_ && spender == e.msg.sender) {
//             assert allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
//         } else {
//             assert allowance(from, spender) == allowanceBefore;
//         }
//     } else if (f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector) {
//         // address from_;
//         // address to_;
//         // uint256 amount;
//         // uint256 deadline_;
//         // uint8 _v;
//         // bytes32 _r;
//         // bytes32 _s;
//         // permit(e, from_, to_, amount, deadline_, _v, _r, _s);
//         // mathint allowanceAfter = allowance(from, spender);
//         // if (from == from_ && spender == e.msg.sender) {
//         //     assert allowanceBefore == max_uint256 || from_ == to_ || allowanceAfter == amount;
//         // } else {
//         //     assert allowance(from, spender) == allowanceBefore;
//         // }
//         assert true;
//     } else
//     {
//         calldataarg args;
//         f(e, args);
//         assert allowance(from, spender) == allowanceBefore;
//     }
// }
// */