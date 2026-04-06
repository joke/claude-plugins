import java.math.BigDecimal;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

public class InventoryService {

    private final ProductRepository productRepository;

    public InventoryService(ProductRepository productRepository) {
        this.productRepository = Objects.requireNonNull(productRepository, "productRepository must not be null");
    }

    public List<Product> findProductsByCategory(String category) {
        Objects.requireNonNull(category, "category must not be null");
        return productRepository.findByCategory(category);
    }

    public BigDecimal calculateTotalStockValue() {
        return productRepository.findAll().stream()
                .map(product -> product.getPrice().multiply(BigDecimal.valueOf(product.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public Optional<Product> findMostExpensiveProduct() {
        return productRepository.findAll().stream()
                .max(Comparator.comparing(Product::getPrice));
    }

    public Map<String, Integer> getStockLevelsByCategory() {
        return productRepository.findAll().stream()
                .collect(Collectors.groupingBy(
                        Product::getCategory,
                        Collectors.summingInt(Product::getQuantity)
                ));
    }
}
