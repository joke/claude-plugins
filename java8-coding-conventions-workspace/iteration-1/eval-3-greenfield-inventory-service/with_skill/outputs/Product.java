import java.math.BigDecimal;
import java.util.Objects;

public class Product {

    private final String id;
    private final String name;
    private final String category;
    private final BigDecimal price;
    private final int quantity;

    public Product(final String id,
                   final String name,
                   final String category,
                   final BigDecimal price,
                   final int quantity) {
        this.id = Objects.requireNonNull(id, "id must not be null");
        this.name = Objects.requireNonNull(name, "name must not be null");
        this.category = Objects.requireNonNull(category, "category must not be null");
        this.price = Objects.requireNonNull(price, "price must not be null");
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

    public BigDecimal stockValue() {
        return price.multiply(BigDecimal.valueOf(quantity));
    }
}
