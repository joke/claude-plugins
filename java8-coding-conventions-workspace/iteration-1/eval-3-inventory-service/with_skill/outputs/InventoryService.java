import java.math.BigDecimal;
import java.util.Collections;
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

    public List<Product> findByCategory(final String category) {
        return Collections.unmodifiableList(
                productRepository.findAll().stream()
                        .filter(product -> product.getCategory().equals(category))
                        .collect(Collectors.toList())
        );
    }

    public BigDecimal calculateTotalStockValue() {
        return productRepository.findAll().stream()
                .map(InventoryService::stockValue)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public Optional<Product> findMostExpensiveProduct() {
        return productRepository.findAll().stream()
                .max(Comparator.comparing(Product::getPrice));
    }

    public Map<String, CategoryStockSummary> getStockSummaryByCategory() {
        final Map<String, List<Product>> grouped = groupByCategory(productRepository.findAll());

        return Collections.unmodifiableMap(
                grouped.entrySet().stream()
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                entry -> buildCategorySummary(entry.getKey(), entry.getValue())
                        ))
        );
    }

    private static Map<String, List<Product>> groupByCategory(final List<Product> products) {
        return products.stream()
                .collect(Collectors.groupingBy(Product::getCategory));
    }

    private static CategoryStockSummary buildCategorySummary(final String category,
                                                             final List<Product> products) {
        final int totalQuantity = products.stream()
                .mapToInt(Product::getQuantity)
                .sum();

        return new CategoryStockSummary(category, totalQuantity, products.size());
    }

    private static BigDecimal stockValue(final Product product) {
        return product.getPrice().multiply(BigDecimal.valueOf(product.getQuantity()));
    }
}
