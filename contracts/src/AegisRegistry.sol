// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title AegisRegistry
/// @notice On-chain, tamper-evident receipts for Aegis decisions.
/// @dev Aegis makes two kinds of deterministic decision off-chain: the firewall
///      verdict on an MCP tool response (allow/flag/block) and the pre-trade
///      scanner verdict on a token (GO/CAUTION/NO). Anyone can anchor a
///      compact commitment of such a decision here so a third party can later
///      verify the agent acted on a real, unmodified verdict — the "on-chain
///      receipt" leg of the shield. The registry stores only hashes; the full
///      report lives off-chain and is proven by preimage.
contract AegisRegistry {
    enum Kind {
        Scan, // pre-trade scanner verdict
        Firewall // firewall verdict on a tool response
    }

    struct Receipt {
        address reporter; // who anchored it
        Kind kind;
        bytes32 subject; // token address (padded) or tool-response hash
        uint8 verdict; // 0=allow/GO 1=flag/CAUTION 2=block/NO 3=unknown
        uint16 score; // risk score at decision time
        bytes32 reportHash; // keccak256 of the full off-chain report JSON
        uint64 timestamp;
    }

    /// @dev receiptId => Receipt. receiptId = keccak256(reporter, subject, reportHash).
    mapping(bytes32 => Receipt) public receipts;

    /// @notice Latest safety badge per repository/agent identifier.
    /// @dev badgeId is an arbitrary keccak of a repo slug or agent id.
    mapping(bytes32 => bytes32) public latestReceiptFor;

    event ReceiptAnchored(
        bytes32 indexed receiptId,
        address indexed reporter,
        Kind kind,
        bytes32 indexed subject,
        uint8 verdict,
        uint16 score,
        bytes32 reportHash
    );

    event BadgeUpdated(bytes32 indexed badgeId, bytes32 receiptId);

    error EmptyReportHash();
    error UnknownReceipt();

    /// @notice Anchor a decision receipt. Idempotent per (reporter, subject, reportHash).
    function anchor(
        Kind kind,
        bytes32 subject,
        uint8 verdict,
        uint16 score,
        bytes32 reportHash
    ) external returns (bytes32 receiptId) {
        if (reportHash == bytes32(0)) revert EmptyReportHash();

        receiptId = keccak256(abi.encodePacked(msg.sender, subject, reportHash));
        receipts[receiptId] = Receipt({
            reporter: msg.sender,
            kind: kind,
            subject: subject,
            verdict: verdict,
            score: score,
            reportHash: reportHash,
            timestamp: uint64(block.timestamp)
        });

        emit ReceiptAnchored(receiptId, msg.sender, kind, subject, verdict, score, reportHash);
    }

    /// @notice Point a repo/agent badge at a previously anchored receipt.
    function setBadge(bytes32 badgeId, bytes32 receiptId) external {
        if (receipts[receiptId].reportHash == bytes32(0)) revert UnknownReceipt();
        latestReceiptFor[badgeId] = receiptId;
        emit BadgeUpdated(badgeId, receiptId);
    }

    /// @notice Verify an off-chain report matches an anchored receipt.
    function verify(bytes32 receiptId, bytes32 reportHash) external view returns (bool) {
        return receipts[receiptId].reportHash == reportHash && reportHash != bytes32(0);
    }
}
