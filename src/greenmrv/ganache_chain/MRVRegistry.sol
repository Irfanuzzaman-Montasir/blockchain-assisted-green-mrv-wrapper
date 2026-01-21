// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract MRVRegistry {

    struct MRVRecord {
        bytes32 hash;
        uint256 timestamp;
        address submitter;
    }

    mapping(string => MRVRecord) private records;

    event MRVRegistered(
        string indexed mrvId,
        bytes32 hash,
        uint256 timestamp,
        address indexed submitter
    );

    function registerMRV(string calldata mrvId, bytes32 hash) external {
        require(bytes(mrvId).length > 0, "MRV ID required");
        require(records[mrvId].timestamp == 0, "MRV already registered");

        records[mrvId] = MRVRecord({
            hash: hash,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        emit MRVRegistered(mrvId, hash, block.timestamp, msg.sender);
    }

    function getMRV(string calldata mrvId)
        external
        view
        returns (bytes32 hash, uint256 timestamp, address submitter)
    {
        MRVRecord memory rec = records[mrvId];
        require(rec.timestamp != 0, "MRV not found");
        return (rec.hash, rec.timestamp, rec.submitter);
    }
}
