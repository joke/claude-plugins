import java.math.BigDecimal;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class InventoryService {

    private final ProductRepository productRepository;

    public InventoryService(final ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> findProductsByCategory(final String category) {
        return productRepository.findByCategory(category);
    }

    public BigDecimal calculateTotalStockValue() {
        return productRepository.findAll().stream()
                .map(Product::getStockValue)
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
