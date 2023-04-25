// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;
 
import {ERC721, Strings} from '@openzeppelin/contracts/token/ERC721/ERC721.sol';
import {ERC721URIStorage} from '@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol';
import {Counters} from '@openzeppelin/contracts/utils/Counters.sol';
import {Ownable} from '@openzeppelin/contracts/access/Ownable.sol';
import {Base64} from '@openzeppelin/contracts/utils/Base64.sol';
 
// Deployed on Mumbai
 
contract bearchainAI is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    using Strings for uint256;
 
    Counters.Counter public _tokenIdCounter;
 
    mapping(uint256 => Fanfic) public tokenIdToFanfic;
    mapping(string => uint256) public authorToKudos;
    string[] public authors;
 
    // NFT base metadata
    string public external_url = 'https://example.com/explore/';
    string public image_data_url = 'https://example.com/api/?tokenId=';
 
    struct Fanfic {
        string title;
        string content;
        string fandom;
        Kudo[] kudos;
    }
 
    struct Kudo {
        string author;
        uint256 cites;
    }
 
    constructor() ERC721('bearchainAI', 'BCHAI') {}
 
    // Methods to change NFT base metadata after deployment if needed
    function setExternalUrl(string memory _url) public onlyOwner {
        external_url = _url;
    }
 
    function setImageDataUrl(string memory _url) public onlyOwner {
        image_data_url = _url;
    }
 
    // Returns total number of authors
    function totalAuthors() public view returns (uint256) {
        return authors.length;
    }
 
 
    /**
     * @dev mints fanfic nft and updates total number of cites for an author
     * @param title title of new fanfic
     * @param content main fanfic content
     * @param kudos list of referenced authors and number of fanfics cited
     */
    function mint(
        string memory title,
        string memory content,
        string memory fandom,
        Kudo[] memory kudos
    ) public {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _safeMint(msg.sender, tokenId);
 
        tokenIdToFanfic[tokenId].title = title;
        tokenIdToFanfic[tokenId].content = content;
        tokenIdToFanfic[tokenId].fandom = fandom;
 
        for (uint i = 0; i < kudos.length; i++) {
            tokenIdToFanfic[tokenId].kudos.push(
                Kudo({author: kudos[i].author, cites: kudos[i].cites})
            );
        }
 
        _setTokenURI(tokenId, tokenURI(tokenId));
 
        for (uint i = 0; i < kudos.length; i++) {
            Kudo memory currentKudo = kudos[i];
 
            if (authorToKudos[currentKudo.author] == 0) {
                authors.push(currentKudo.author);
            }
 
            authorToKudos[kudos[i].author] += kudos[i].cites;
        }
    }
 
    /**
     * @dev overrides default tokenURI and returns in base64 json format
     * @param tokenId returns uri for the specified tokenid
     */
    function tokenURI(
        uint256 tokenId
    ) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        require(
            _exists(tokenId),
            'ERC721Metadata: URI query for nonexistent token'
        );
 
        string memory tokenString = tokenId.toString();
        Fanfic memory fanfic = tokenIdToFanfic[tokenId];
 
        // must escape json strings when minting! else this will break
        bytes memory json = abi.encodePacked(
            '{',
            '"name": "Fanfic #',
            tokenString,
            ': ',
            fanfic.title,
            '",',
            '"description": "',
            fanfic.content,
            '",',
            '"external_url": "',
            external_url,
            tokenString,
            '",',
            '"image_data": "',
            image_data_url,
            tokenString,
            '",',
            '"attributes": [',
            _kudosToAttributeString(fanfic.kudos),
            '{"trait_type" : "Fandom", "value": "',
            fanfic.fandom,
            '"}',
            ']'
            '}'
        );
 
        return
            string(
                abi.encodePacked(
                    'data:application/json;base64,',
                    Base64.encode(json)
                )
            );
    }
 
    /**
     * @dev creates json strin of kudos attributes
     * @param kudos list of all kudo structs
     */
    function _kudosToAttributeString(
        Kudo[] memory kudos
    ) internal pure returns (string memory) {
        string memory kudosJSON = '';
        for (uint i = 0; i < kudos.length; i++) {
            kudosJSON = string.concat(
                kudosJSON,
                '{"trait_type": "',
                kudos[i].author,
                '", "value": ',
                kudos[i].cites.toString(),
                '},'
            );
        }
        return kudosJSON;
    }
 
    // The following functions are overrides required by Solidity.
    function _burn(
        uint256 tokenId
    ) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
}