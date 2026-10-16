pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);

    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract Pool {
    IERC20 public token;
}

contract TokenOps {
    struct Wallet {
        address addr;
    }

    IERC20 public token;
    Pool public pool;
    Wallet[] public wallets;
    address public recipient = address(0xBEEF);

    function uncheckedParam(IERC20 t, uint256 amount) public {
        t.transfer(recipient, amount);
    }

    function uncheckedState(uint256 amount) public {
        token.transfer(recipient, amount);
    }

    function uncheckedCast(address t, uint256 amount) public {
        IERC20(t).transfer(recipient, amount);
    }

    function uncheckedMemberChain(uint256 amount) public {
        pool.token.transfer(recipient, amount);
    }

    function checked(IERC20 t, uint256 amount) public {
        require(t.transfer(recipient, amount), "transfer failed");
    }

    function ownFunctionCall(uint256 amount) public {
        this.transfer(recipient, amount);
    }

    function transfer(address to, uint256 amount) public {
        token.transfer(to, amount);
    }

    function etherTransfers(uint256 amount) public {
        payable(recipient).transfer(amount);
        msg.sender.transfer(amount);
        address(this).transfer(amount);
        wallets[0].addr.transfer(amount);
    }
}
