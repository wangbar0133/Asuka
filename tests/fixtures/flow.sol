pragma solidity ^0.8.0;

interface IFoo {
    function bar() external returns (bool);
}

contract Flow is IFoo {
    uint256 public total;

    function bar() external returns (bool) {
        try Flow(address(this)).bar() returns (bool ok) {
            return ok;
        } catch Error(string memory reason) {
            revert(reason);
        } catch (bytes memory) {
            return false;
        }
    }

    function f(uint256 x) public returns (uint256) {
        if (x > 10) {
            total = x * 2;
        } else {
            total = 1;
        }
        while (total > 0) {
            total = total - 1;
        }
        for (uint256 i = 0; i < x; i++) {
            total = total + i;
        }
        uint256 j = 0;
        j++;
        j--;
        return j;
    }

    function g(uint256 n) public pure returns (uint256) {
        uint256 sum = 0;
        // single-statement (non-block) for body
        for (uint256 i = 0; i < n; i++) sum = sum + 1;
        // index access whose base is a function call
        uint256 first = getList()[0];
        return sum + first;
    }

    function getList() internal pure returns (uint256[] memory) {
        uint256[] memory list = new uint256[](1);
        list[0] = 42;
        return list;
    }
}
