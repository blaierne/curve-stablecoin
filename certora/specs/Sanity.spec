
rule sanity(method f, calldataarg args, env e) {
    f(e,args);

    satisfy(true);
}
