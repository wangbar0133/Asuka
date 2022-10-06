pragma solidity 0.4.24;

contract MyContract {

    address owner;

    function MyContract() public {
        owner = msg.sender;
    }

    function sendTo(address receiver, uint amount) public {
        require(tx.origin == owner);
        require(tx.origin != msg.sender)
        receiver.transfer(amount);
    }

}