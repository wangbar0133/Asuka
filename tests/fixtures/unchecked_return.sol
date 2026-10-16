pragma solidity ^0.8.0;

contract Ret {
    address public token;

    function checked(address target) public returns (bool) {
        (bool success, ) = target.call("");
        require(success);
        return success;
    }

    function uncheckedVar(address target) public returns (bool) {
        (bool sent, ) = target.call("");
        return sent;
    }

    function mixed(address target, uint256 amount) public returns (uint256) {
        target.call("");
        uint256 plain = amount;
        uint256 viaCall = pick();
        return plain + viaCall;
    }

    function guards(address target, uint256 amount) public returns (bool) {
        (bool ok, ) = target.call("");
        // member-access call: not require()
        token.balanceOf(address(0));
        // identifier call: not require()
        pick();
        // plain assignment: not a call at all
        uint256 other = amount;
        other = 0;
        // require variants that must NOT clear the map
        require(42);
        require(other);
        require();
        // variable initialized from a member call outside METHED
        uint256 bal = token.balanceOf(address(0));
        return ok;
    }

    function pick() internal returns (uint256) {
        return 1;
    }
}
