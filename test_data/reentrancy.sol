pragma solidity 0.4.24;

contract SimpleDAO {
  mapping (address => uint) public credit;
  uint256 balance = 0;

    struct MapEntry {
        uint256 _key;
        uint256 _value;
    }
  function donate(address to) payable nonReentrant public{
    credit[to] += msg.value;
  }
    
  function add(UintSet storage set, uint256 ) internal returns (bool) {
        return _add(set._inner, bytes32(value));
  }

  function withdraw(uint amount) public{
    if (credit[msg.sender]>= amount) {
      require(msg.sender.call.value(amount)());
      credit[msg.sender]-=amount;
      
      
    }
  }  

  function withdraw1(uint256 amount) public {
    require(msg.sender.call.value(amount)());
    balance = amount;
  }

  function withdraw2(uint256 amount) public {
    require(msg.sender.call.value(amount)());
    MapEntry storage me = credit[msg.sender];
    me._key = amount;
  }
}
