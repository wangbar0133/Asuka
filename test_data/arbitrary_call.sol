pragma solidity ^0.8.0;

contract arbitraryCall {
    address public immutable zeroXExchangeProxy;

    function vul(address token, address from, uint256 amount) public {
        IERC20(token).transferFrom(from, address(this), amount);
    }

    function vul1(bytes calldata swapData) public {
        (bool success, ) = zeroXExchangeProxy.call(swapData);
    }

    function approveToken(address _token, address _spender) external onlyGov {
        IERC20(_token).approve(_spender, type(uint256).max);
    }
}