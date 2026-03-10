from typing import Optional, Dict, Any

class Product:
    def __init__(self, title: str, description: str, url: str, 
                 price: Optional[str] = None, seller: Optional[str] = None, 
                 image_url: Optional[str] = None):
        if not isinstance(title, str):
            raise TypeError("title必须是字符串")
        if not isinstance(description, str):
            raise TypeError("description必须是字符串")
        if not isinstance(url, str):
            raise TypeError("url必须是字符串")
        self.title = title
        self.description = description
        self.url = url
        self.price = price
        self.seller = seller
        self.image_url = image_url
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "price": self.price,
            "seller": self.seller,
            "image_url": self.image_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        if not isinstance(data, dict):
            raise TypeError("data必须是字典")
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            price=data.get("price"),
            seller=data.get("seller"),
            image_url=data.get("image_url")
        )
    
    def __str__(self):
        return f"{(self.title or '')} - {(self.price or '价格未知')}"