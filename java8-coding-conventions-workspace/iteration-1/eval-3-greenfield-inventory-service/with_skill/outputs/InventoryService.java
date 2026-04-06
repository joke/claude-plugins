import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

public class InventoryService {

    private final ProductRepository productRepository;

    public InventoryService(final ProductRepository productRepository) {
        this.productRepository = Objects.requireNonNull(productRepository, "productRepository must not be null");
    }

    public List<Product> findByCategory(final String category) {
        return productRepository.findAll().stream()
                .filter(product -> product.getCategory().equals(category))
                .collect(Collectors.toList());
    }

    public BigDecimal calculateTotalStockValue() {
        return productRepository.findAll().stream()
                .map(Product::stockValue)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public Optional<Product> findMostExpensive() {
        return productRepository.findAll().stream()
                .max(this::compareByPrice);
    }

    public Map<String, Long> summarizeStockByCategory() {
        return productRepository.findAll().stream()
                .collect(Collectors.groupingBy(Product::getCategory, Collectors.summingLong(Product::getQuantity)));
    }

    private int compareByPrice(final Product first, final Product second) {
        return first.getPrice().compareTo(second.getPrice());
    }
}
