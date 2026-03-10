class Product:
    def __init__(self, title, description, url, price=None, seller=None, image_url=None):
        self.title = title
        self.description = description
        self.url = url
        self.price = price
        self.seller = seller
        self.image_url = image_url
    
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "price": self.price,
            "seller": self.seller,
            "image_url": self.image_url
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            price=data.get("price"),
            seller=data.get("seller"),
            image_url=data.get("image_url")
        )
    
    def __str__(self):
        return f"{self.title} - {self.price or '价格未知'}"