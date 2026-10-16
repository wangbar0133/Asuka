pragma solidity ^0.8.0;

contract Suicidal {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function bad() public {
        selfdestruct(owner);
    }

    function good() public onlyOwner {
        selfdestruct(owner);
    }

    function internalOnly() internal {
        selfdestruct(owner);
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }
}
