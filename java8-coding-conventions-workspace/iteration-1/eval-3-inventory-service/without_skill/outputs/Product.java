import java.math.BigDecimal;

public final class Product {

    private final String id;
    private final String name;
    private final String category;
    private final BigDecimal price;
    private final int quantity;

    public Product(final String id, final String name, final String category, final BigDecimal price, final int quantity) {
        this.id = id;
        this.name = name;
        this.category = category;
        this.price = price;
        this.quantity = quantity;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getCategory() {
        return category;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public int getQuantity() {
        return quantity;
    }

    public BigDecimal getStockValue() {
        return price.multiply(BigDecimal.valueOf(quantity));
    }
}
