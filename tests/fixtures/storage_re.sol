pragma solidity ^0.8.0;

contract StorageRe {
    struct S {
        uint256 v;
    }

    mapping(address => S) public data;
    mapping(uint256 => uint256) public scores;
    uint256 public total;

    function withdraw(uint256 amount) public {
        require(msg.sender.call(""));
        // non-binary statement after the low-level call
        this.ping();
        // storage pointer member write after the low-level call
        S storage s = data[msg.sender];
        s.v = amount;
        // member access on a non-identifier base (index access)
        data[msg.sender].v = amount;
        total = amount;
    }

    function ping() public {
        // index access whose base is a member access (this.scores)
        this.scores[0] = 1;
    }

    function getView(address t) public view {
        t.call("");
    }
}
