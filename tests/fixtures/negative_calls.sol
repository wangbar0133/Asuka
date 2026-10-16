pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

contract NegativeCalls {
    address public proxy;

    // bare delegatecall() call: no callee expression - must not crash
    function forward(bytes memory data) public {
        delegatecall(data);
    }

    // view function: skipped before any call analysis
    function getInfo(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }

    // near-misses for the IERC20(token).transferFrom(...) pattern
    function twoArgs(uint256 a, uint256 b) public {
        IERC20(a, b).transfer(address(this), 0);
    }

    function nonIdentifierArg(uint256 amount) public {
        IERC20(42).transfer(address(this), amount);
    }

    function nonParameterArg() public {
        IERC20(proxy).transfer(address(this), 0);
    }

    function notAnAddress(uint256 token) public {
        IERC20(token).transfer(address(this), 0);
    }

    function calleeIsCall(address token) public {
        IERC20(this.pick()).transfer(address(this), 0);
    }

    // near-misses for the x.call(data) pattern
    function callNonIdentifier(bytes memory data) public {
        proxy.call(abi.encode(data));
    }

    function callLocalVar() public {
        bytes memory local = "";
        proxy.call(local);
    }

    function callNonBytes(uint256 data) public {
        proxy.call(data);
    }

    function pick() internal returns (address) {
        return proxy;
    }
}
