pragma solidity ^0.8.0;

contract Arithmetic {
    uint256 public a = 100;
    uint256 public b = 7;
    uint256 public c = 3;
    bool public flag = true;

    function dividedMultiply() public view returns (uint256) {
        return a / b * c;
    }

    function moduloMultiply() public view returns (uint256) {
        return a % b * c;
    }

    function properOrder() public view returns (uint256) {
        return a * c / b;
    }

    function plainMaths() public view returns (uint256) {
        return a / b + c * a;
    }

    function tautological(uint256 x) public view returns (bool) {
        return x == x;
    }

    function memberTautology() public view returns (bool) {
        return a == a;
    }

    function memberChainTautology() public view returns (bool) {
        return this.flag == this.flag;
    }

    function realComparison(uint256 x, uint256 y) public view returns (bool) {
        return x == y;
    }

    function dangerousUnary() public view returns (bool) {
        return !flag == true;
    }

    function dangerousBitwise(uint8 z) public view returns (bool) {
        return ~z > 3;
    }

    function harmlessUnary() public pure returns (bool) {
        return !true;
    }
}
