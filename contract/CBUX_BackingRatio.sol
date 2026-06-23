
# contracts/CBUX_BackingRatio.sol
sol_cbux = """// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// CBU-X Backing Ratio — On-chain verification of physical backing

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CBUXToken is ERC20, Ownable {
    uint256 public constant SCALE_PHYSICAL = 10**18;
    uint256 public constant SCALE_CBU = 10**6;
    
    uint256 public physicalValue;  // Total physical backing in USD * SCALE
    uint256 public totalCBU;       // Total CBU supply
    
    enum BackingLevel { GREEN, YELLOW, ORANGE, RED }
    
    event BackingUpdated(uint256 physicalValue, uint256 totalCBU, uint256 ratio);
    event FreezeGradual(BackingLevel level, uint256 taxRate);
    
    constructor() ERC20("CBU-X", "CBUX") Ownable(msg.sender) {}
    
    function updateBacking(uint256 _physicalValue, uint256 _totalCBU) external onlyOwner {
        physicalValue = _physicalValue;
        totalCBU = _totalCBU;
        emit BackingUpdated(_physicalValue, _totalCBU, backingRatio());
    }
    
    function backingRatio() public view returns (uint256) {
        if (totalCBU == 0) return SCALE_PHYSICAL;
        return (physicalValue * SCALE_PHYSICAL) / (totalCBU * SCALE_CBU);
    }
    
    function getBackingLevel() public view returns (BackingLevel) {
        uint256 ratio = backingRatio();
        if (ratio >= SCALE_PHYSICAL) return BackingLevel.GREEN;
        if (ratio >= 8 * SCALE_PHYSICAL / 10) return BackingLevel.YELLOW;
        if (ratio >= 5 * SCALE_PHYSICAL / 10) return BackingLevel.ORANGE;
        return BackingLevel.RED;
    }
    
    function mint(address to, uint256 amount) external onlyOwner {
        BackingLevel level = getBackingLevel();
        uint256 tax = 0;
        
        if (level == BackingLevel.YELLOW) {
            tax = amount * (SCALE_PHYSICAL - backingRatio()) * 20 / SCALE_PHYSICAL / 100;
        } else if (level == BackingLevel.ORANGE) {
            require(amount <= 1000 * SCALE_CBU, "Daily limit exceeded");
        } else if (level == BackingLevel.RED) {
            revert("Complete freeze — restructuring required");
        }
        
        _mint(to, amount - tax);
        if (tax > 0) _mint(owner(), tax);
        totalCBU += amount;
        
        emit FreezeGradual(level, tax);
    }
    
    function burn(address from, uint256 amount) external onlyOwner {
        _burn(from, amount);
        totalCBU -= amount;
    }
}
"""

with open("/mnt/agents/output/yusuf-grondona-system/contracts/CBUX_BackingRatio.sol", "w") as f:
    f.write(sol_cbux)

# contracts/ConvertibilityRegistry.sol
sol_convert = """// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Convertibility Registry — Corridors for X/CBU exchange

pragma solidity ^0.8.20;

contract ConvertibilityRegistry {
    struct Corridor {
        address zone;
        uint256 floorRate;     // Minimum X per CBU
        uint256 ceilingRate;   // Maximum X per CBU
        bool active;
    }
    
    mapping(bytes32 => Corridor) public corridors;
    bytes32[] public corridorList;
    
    event CorridorAdded(bytes32 indexed id, address zone, uint256 floor, uint256 ceiling);
    event RateUpdated(bytes32 indexed id, uint256 newFloor, uint256 newCeiling);
    
    function addCorridor(bytes32 id, address zone, uint256 floor, uint256 ceiling) external {
        require(floor < ceiling, "Invalid spread");
        corridors[id] = Corridor(zone, floor, ceiling, true);
        corridorList.push(id);
        emit CorridorAdded(id, zone, floor, ceiling);
    }
    
    function updateRates(bytes32 id, uint256 floor, uint256 ceiling) external {
        require(corridors[id].active, "Corridor inactive");
        corridors[id].floorRate = floor;
        corridors[id].ceilingRate = ceiling;
        emit RateUpdated(id, floor, ceiling);
    }
    
    function getValidRate(bytes32 id, uint256 proposedRate) external view returns (bool) {
        Corridor memory c = corridors[id];
        return c.active && proposedRate >= c.floorRate && proposedRate <= c.ceilingRate;
    }
}
"""

with open("/mnt/agents/output/yusuf-grondona-system/contracts/ConvertibilityRegistry.sol", "w") as f:
    f.write(sol_convert)

# contracts/YusufLending.sol
sol_lending = """// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Yusuf Lending — Interest-free lending with profit-sharing

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract YusufLending {
    struct Loan {
        address borrower;
        uint256 principal;
        uint256 profitShare;  // Basis points (e.g., 3000 = 30%)
        uint256 repaid;
        bool active;
    }
    
    mapping(uint256 => Loan) public loans;
    uint256 public loanCounter;
    IERC20 public token;
    
    event LoanCreated(uint256 indexed id, address borrower, uint256 principal);
    event ProfitDistributed(uint256 indexed id, uint256 profit);
    
    constructor(address _token) {
        token = IERC20(_token);
    }
    
    function createLoan(address borrower, uint256 principal, uint256 profitShareBps) external {
        require(profitShareBps <= 5000, "Max 50% profit share");
        require(token.transferFrom(msg.sender, borrower, principal), "Transfer failed");
        
        loanCounter++;
        loans[loanCounter] = Loan(borrower, principal, profitShareBps, 0, true);
        emit LoanCreated(loanCounter, borrower, principal);
    }
    
    function distributeProfit(uint256 loanId, uint256 totalProfit) external {
        Loan storage l = loans[loanId];
        require(l.active, "Loan inactive");
        
        uint256 lenderShare = totalProfit * (10000 - l.profitShare) / 10000;
        uint256 borrowerShare = totalProfit - lenderShare;
        
        require(token.transferFrom(l.borrower, msg.sender, lenderShare + l.principal), "Repayment failed");
        
        l.repaid += l.principal + lenderShare;
        l.active = false;
        
        emit ProfitDistributed(loanId, totalProfit);
    }
}
"""

with open("/mnt/agents/output/yusuf-grondona-system/contracts/YusufLending.sol", "w") as f:
    f.write(sol_lending)

# contracts/ZakatAudit.sol
sol_zakat = """// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Zakat Audit — On-chain Zakat collection and distribution

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ZakatAudit is Ownable {
    enum Category {
        AL_FUQARA,    // Poor
        AL_MASAKIN,   // Needy
        AL_AMILIN,    // Collectors
        AL_MUALLAFATI,// Hearts to reconcile
        FI_AL_RIQAB,  // Freed slaves
        AL_GHARIMIN,  // Debtors
        FI_SABILILLAH,// In the path of God
        IBN_AL_SABIL  // Wayfarers
    }
    
    struct Distribution {
        Category category;
        uint256 amount;
        address recipient;
        uint256 timestamp;
    }
    
    IERC20 public nuqudToken;
    uint256 public totalCollected;
    uint256 public totalDistributed;
    Distribution[] public distributions;
    
    mapping(address => uint256) public zakatPaid;
    
    event ZakatCollected(address indexed payer, uint256 amount);
    event ZakatDistributed(Category indexed category, uint256 amount, address recipient);
    
    constructor(address _nuqudToken) Ownable(msg.sender) {
        nuqudToken = IERC20(_nuqudToken);
    }
    
    function payZakat(uint256 amount) external {
        require(nuqudToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        totalCollected += amount;
        zakatPaid[msg.sender] += amount;
        emit ZakatCollected(msg.sender, amount);
    }
    
    function distribute(Category category, uint256 amount, address recipient) external onlyOwner {
        require(amount <= totalCollected - totalDistributed, "Insufficient funds");
        require(nuqudToken.transfer(recipient, amount), "Distribution failed");
        
        totalDistributed += amount;
        distributions.push(Distribution(category, amount, recipient, block.timestamp));
        
        emit ZakatDistributed(category, amount, recipient);
    }
    
    function autoDistribute(address[8] memory recipients) external onlyOwner {
        uint256 share = (totalCollected - totalDistributed) / 8;
        require(share > 0, "Nothing to distribute");
        
        for (uint i = 0; i < 8; i++) {
            distribute(Category(i), share, recipients[i]);
        }
    }
    
    function getReport() external view returns (uint256, uint256, uint256) {
        return (totalCollected, totalDistributed, distributions.length);
    }
}
"""

with open("/mnt/agents/output/yusuf-grondona-system/contracts/ZakatAudit.sol", "w") as f:
    f.write(sol_zakat)

# contracts/crd_nuqud.sol
sol_crd = """// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// CRD + Nuqud Tokenization — Commodity Reserve with gold/silver backing

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NuqudToken is ERC20, Ownable {
    string private _metalType;
    uint256 private _totalReserve;
    
    constructor(string memory name, string memory symbol, string memory metalType)
        ERC20(name, symbol) Ownable(msg.sender) {
        _metalType = metalType;
        _totalReserve = 0;
    }
    
    function mint(address to, uint256 grams) external onlyOwner {
        require(grams > 0, "Amount must be positive");
        _mint(to, grams);
        _totalReserve += grams;
    }
    
    function burn(address from, uint256 grams) external onlyOwner {
        require(balanceOf(from) >= grams, "Insufficient balance");
        _burn(from, grams);
        _totalReserve -= grams;
    }
    
    function totalReserve() external view returns (uint256) {
        return _totalReserve;
    }
    
    function metalType() external view returns (string memory) {
        return _metalType;
    }
}

contract CRD is Ownable {
    struct Commodity {
        uint256 floorPrice;
        uint256 ceilingPrice;
        uint256 stockpile;
    }
    
    mapping(string => Commodity) public commodities;
    mapping(address => uint256) public fulusBalances;
    uint256 public totalFulusSupply;
    
    event CRDBuy(address indexed buyer, string commodity, uint256 grams, uint256 fulusCreated);
    event CRDSell(address indexed seller, string commodity, uint256 grams, uint256 fulusDestroyed);
    
    constructor() Ownable(msg.sender) {
        commodities["gold"] = Commodity(50, 70, 0);
        commodities["silver"] = Commodity(8, 12, 0);
        commodities["copper"] = Commodity(8000, 12000, 0);
        commodities["wheat"] = Commodity(180, 220, 0);
    }
    
    function buyCommodity(string memory commodity, uint256 grams) external {
        Commodity storage c = commodities[commodity];
        require(c.floorPrice > 0, "Commodity not supported");
        
        uint256 fulusCreated = grams * c.floorPrice;
        fulusBalances[msg.sender] += fulusCreated;
        totalFulusSupply += fulusCreated;
        c.stockpile += grams;
        
        emit CRDBuy(msg.sender, commodity, grams, fulusCreated);
    }
    
    function sellCommodity(string memory commodity, uint256 grams) external {
        Commodity storage c = commodities[commodity];
        require(c.stockpile >= grams, "Insufficient stockpile");
        
        uint256 fulusDestroyed = grams * c.ceilingPrice;
        require(fulusBalances[msg.sender] >= fulusDestroyed, "Insufficient fulus");
        
        fulusBalances[msg.sender] -= fulusDestroyed;
        totalFulusSupply -= fulusDestroyed;
        c.stockpile -= grams;
        
        emit CRDSell(msg.sender, commodity, grams, fulusDestroyed);
    }
    
    function transferFulus(address to, uint256 amount) external {
        require(fulusBalances[msg.sender] >= amount, "Insufficient fulus");
        fulusBalances[msg.sender] -= amount;
        fulusBalances[to] += amount;
    }
}
"""

with open("/mnt/agents/output/yusuf-grondona-system/contracts/crd_nuqud.sol", "w") as f:
    f.write(sol_crd)

# contracts/commenda.sol
sol_commenda = """// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Commenda (Qirad/Mudaraba) — Islamic profit-sharing contract

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Commenda is Ownable {
    struct Deal {
        address mudarib;
        uint256 totalCapital;
        uint256 profitShareMudarib;
        uint256 repaidAmount;
        bool active;
    }
    
    IERC20 public nuqudToken;
    uint256 public dealCounter;
    mapping(uint256 => Deal) public deals;
    mapping(uint256 => mapping(address => uint256)) public investorShares;
    
    event DealCreated(uint256 indexed dealId, address mudarib, uint256 totalCapital);
    event ProfitDistributed(uint256 indexed dealId, uint256 totalProfit);
    
    constructor(address _nuqudToken) Ownable(msg.sender) {
        nuqudToken = IERC20(_nuqudToken);
    }
    
    function createDeal(
        address mudarib,
        uint256 totalCapital,
        uint256 profitShareMudarib
    ) external onlyOwner returns (uint256) {
        require(totalCapital > 0, "Capital must be positive");
        require(profitShareMudarib <= 5000, "Mudarib share cannot exceed 50%");
        
        uint256 dealId = ++dealCounter;
        deals[dealId] = Deal({
            mudarib: mudarib,
            totalCapital: totalCapital,
            profitShareMudarib: profitShareMudarib,
            repaidAmount: 0,
            active: true
        });
        emit DealCreated(dealId, mudarib, totalCapital);
        return dealId;
    }
    
    function invest(uint256 dealId, uint256 amount) external {
        Deal storage d = deals[dealId];
        require(d.active, "Deal not active");
        require(nuqudToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        investorShares[dealId][msg.sender] += amount;
    }
    
    function distributeProfit(uint256 dealId, uint256 totalProfit) external onlyOwner {
        Deal storage d = deals[dealId];
        require(d.active, "Deal not active");
        
        uint256 mudaribShare = (totalProfit * d.profitShareMudarib) / 10000;
        uint256 investorsShare = totalProfit - mudaribShare;
        
        require(nuqudToken.transfer(d.mudarib, mudaribShare), "Mudarib transfer failed");
        
        d.repaidAmount += totalProfit;
        emit ProfitDistributed(dealId, totalProfit);
    }
    
    function closeDeal(uint256 dealId) external onlyOwner {
        Deal storage d = deals[dealId];
        require(d.active, "Already closed");
        require(d.repaidAmount >= d.totalCapital, "Capital not fully returned");
        d.active = false;
    }
}
"""

with open("/mnt/agents/output/yusuf-grondona-system/contracts/commenda.sol", "w") as f:
    f.write(sol_commenda)

print("6 smart contracts Solidity créés")