// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ERC20 {
    function transfer(address to, uint256 value) external returns (bool);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Transfer(address indexed sender, address indexed receiver, uint256 value);
}

interface ERC1271 {
    function isValidSignature(bytes32 hash, bytes calldata signature) external view returns (bytes4);
}

contract crvUSD is ERC20 {
    uint8 public constant decimals = 18;
    string public constant version = "v1.0.0";

    bytes4 private constant ERC1271_MAGIC_VAL = 0x1626ba7e;
    bytes32 private constant EIP712_TYPEHASH = keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)");
    bytes32 private constant EIP2612_TYPEHASH = keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");
    bytes32 private constant VERSION_HASH = keccak256(bytes(version));

    string public immutable name;
    string public immutable symbol;
    bytes32 public immutable salt;

    bytes32 public immutable NAME_HASH;
    uint256 public immutable CACHED_CHAIN_ID;
    bytes32 public immutable CACHED_DOMAIN_SEPARATOR;

    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;
    mapping(address => uint256) public nonces;
    address public minter;

    event SetMinter(address indexed minter);

    constructor(string memory _name, string memory _symbol) {
        name = _name;
        symbol = _symbol;

        NAME_HASH = keccak256(bytes(_name));
        CACHED_CHAIN_ID = block.chainid;
        salt = blockhash(block.number - 1);
        CACHED_DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                EIP712_TYPEHASH,
                keccak256(bytes(_name)),
                VERSION_HASH,
                block.chainid,
                address(this),
                blockhash(block.number - 1)
            )
        );

        minter = msg.sender;
        emit SetMinter(msg.sender);
    }

    function _approve(address _owner, address _spender, uint256 _value) internal {
        allowance[_owner][_spender] = _value;
        emit Approval(_owner, _spender, _value);
    }

    function _burn(address _from, uint256 _value) internal {
        balanceOf[_from] -= _value;
        totalSupply -= _value;
        emit Transfer(_from, address(0), _value);
    }

    function _transfer(address _from, address _to, uint256 _value) internal {
        require(_to != address(this) && _to != address(0), "Invalid transfer destination");
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(_from, _to, _value);
    }

    function _domain_separator() internal view returns (bytes32) {
        if (block.chainid != CACHED_CHAIN_ID) {
            return keccak256(
                abi.encode(
                    EIP712_TYPEHASH,
                    NAME_HASH,
                    VERSION_HASH,
                    block.chainid,
                    address(this),
                    salt
                )
            );
        }
        return CACHED_DOMAIN_SEPARATOR;
    }

    function transferFrom(address _from, address _to, uint256 _value) external override returns (bool) {
        uint256 allowanceAmount = allowance[_from][msg.sender];
        if (allowanceAmount != type(uint256).max) {
            _approve(_from, msg.sender, allowanceAmount - _value);
        }

        _transfer(_from, _to, _value);
        return true;
    }

    function transfer(address _to, uint256 _value) external override returns (bool) {
        _transfer(msg.sender, _to, _value);
        return true;
    }

    function approve(address _spender, uint256 _value) external override returns (bool) {
        _approve(msg.sender, _spender, _value);
        return true;
    }

    function permit(
        address _owner,
        address _spender,
        uint256 _value,
        uint256 _deadline,
        uint8 _v,
        bytes32 _r,
        bytes32 _s
    ) external override returns (bool) {
        require(_owner != address(0) && block.timestamp <= _deadline, "Invalid owner or deadline");

        uint256 nonce = nonces[_owner];
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                _domain_separator(),
                keccak256(
                    abi.encode(
                        EIP2612_TYPEHASH,
                        _owner,
                        _spender,
                        _value,
                        nonce,
                        _deadline
                    )
                )
            )
        );

        if (_owner.isContract()) {
            bytes memory sig = abi.encode(_r, _s);
            require(ERC1271(_owner).isValidSignature(digest, sig) == ERC1271_MAGIC_VAL, "Invalid signature");
        } else {
            require(ecrecover(digest, _v, _r, _s) == _owner, "Invalid signature");
        }

        nonces[_owner] = nonce + 1;
        _approve(_owner, _spender, _value);
        return true;
    }

    function increaseAllowance(address _spender, uint256 _addValue) external override returns (bool) {
        uint256 cachedAllowance = allowance[msg.sender][_spender];
        uint256 newAllowance = cachedAllowance + _addValue;

        if (newAllowance < cachedAllowance) {
            newAllowance = type(uint256).max;
        }

        if (newAllowance != cachedAllowance) {
            _approve(msg.sender, _spender, newAllowance);
        }

        return true;
    }

    function decreaseAllowance(address _spender, uint256 _subValue) external override returns (bool) {
        uint256 cachedAllowance = allowance[msg.sender][_spender];
        uint256 newAllowance = cachedAllowance - _subValue;

        if (cachedAllowance < newAllowance) {
            newAllowance = 0;
        }

        if (newAllowance != cachedAllowance) {
            _approve(msg.sender, _spender, newAllowance);
        }

        return true;
    }

    function burnFrom(address _from, uint256 _value) external override returns (bool) {
        uint256 allowanceAmount = allowance[_from][msg.sender];
        if (allowanceAmount != type(uint256).max) {
            _approve(_from, msg.sender, allowanceAmount - _value);
        }

        _burn(_from, _value);
        return true;
    }

    function burn(uint256 _value) external override returns (bool) {
        _burn(msg.sender, _value);
        return true;
    }

    function mint(address _to, uint256 _value) external override returns (bool) {
        require(msg.sender == minter && _to != address(this) && _to != address(0), "Invalid mint parameters");

        balanceOf[_to] += _value;
        totalSupply += _value;
        emit Transfer(address(0), _to, _value);

        return true;
    }

    function setMinter(address _minter) external {
        require(msg.sender == minter, "Not authorized to set minter");
        minter = _minter;
        emit SetMinter(_minter);
    }

    function DOMAIN_SEPARATOR() external view returns (bytes32) {
        return _domain_separator();
    }
}
