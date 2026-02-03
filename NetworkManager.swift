import Foundation
import Combine

// MARK: - Error Types
enum NetworkError: LocalizedError {
    case invalidURL
    case invalidResponse
    case decodingError(String)
    case serverError(Int)
    case noInternet
    case timeout
    case unknown(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "The URL provided was invalid."
        case .invalidResponse:
            return "The server response was invalid."
        case .decodingError(let reason):
            return "Failed to decode response: \(reason)"
        case .serverError(let code):
            return "Server error: \(code)"
        case .noInternet:
            return "No internet connection available."
        case .timeout:
            return "Request timed out."
        case .unknown(let error):
            return "Unknown error: \(error.localizedDescription)"
        }
    }
}

// MARK: - Request Configuration
struct NetworkRequest {
    let url: URL
    let method: HTTPMethod
    let headers: [String: String]?
    let body: Data?
    let timeoutInterval: TimeInterval
    let retryPolicy: RetryPolicy
    
    init(
        url: URL,
        method: HTTPMethod = .get,
        headers: [String: String]? = nil,
        body: Data? = nil,
        timeoutInterval: TimeInterval = 30,
        retryPolicy: RetryPolicy = .default
    ) {
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.timeoutInterval = timeoutInterval
        self.retryPolicy = retryPolicy
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

struct RetryPolicy {
    let maxRetries: Int
    let backoffMultiplier: Double
    let initialDelay: TimeInterval
    
    static let `default` = RetryPolicy(
        maxRetries: 3,
        backoffMultiplier: 2.0,
        initialDelay: 1.0
    )
    
    static let aggressive = RetryPolicy(
        maxRetries: 5,
        backoffMultiplier: 1.5,
        initialDelay: 0.5
    )
    
    static let none = RetryPolicy(
        maxRetries: 0,
        backoffMultiplier: 1.0,
        initialDelay: 0
    )
}

// MARK: - Cache Protocol
protocol NetworkCacheProtocol {
    func getCached<T: Codable>(for key: String) -> T?
    func cache<T: Codable>(_ object: T, for key: String)
    func removeCache(for key: String)
    func clearAllCache()
}

// MARK: - Simple Memory Cache Implementation
class NetworkMemoryCache: NetworkCacheProtocol {
    private var cache: [String: Any] = [:]
    private let queue = DispatchQueue(label: "com.network.cache", attributes: .concurrent)
    
    func getCached<T: Codable>(for key: String) -> T? {
        queue.sync {
            cache[key] as? T
        }
    }
    
    func cache<T: Codable>(_ object: T, for key: String) {
        queue.async(flags: .barrier) {
            self.cache[key] = object
        }
    }
    
    func removeCache(for key: String) {
        queue.async(flags: .barrier) {
            self.cache.removeValue(forKey: key)
        }
    }
    
    func clearAllCache() {
        queue.async(flags: .barrier) {
            self.cache.removeAll()
        }
    }
}

// MARK: - Network Manager (Protocol-Oriented)
protocol NetworkManagerProtocol {
    associatedtype T: Codable
    
    func request<T: Codable>(_ networkRequest: NetworkRequest) async throws -> T
    func requestWithProgress<T: Codable>(
        _ networkRequest: NetworkRequest,
        progressHandler: @escaping (Double) -> Void
    ) async throws -> T
}

// MARK: - Main NetworkManager
actor NetworkManager {
    static let shared = NetworkManager()
    
    private let session: URLSession
    private let cache: NetworkCacheProtocol
    private let jsonDecoder: JSONDecoder
    private let logger: NetworkLogger
    
    // Concurrent request tracking
    private var activeRequests: [String: Task<Void, Never>] = [:]
    
    init(
        cache: NetworkCacheProtocol = NetworkMemoryCache(),
        logger: NetworkLogger = NetworkLogger()
    ) {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        config.waitsForConnectivity = true
        config.shouldUseExtendedBackgroundIdleMode = true
        
        self.session = URLSession(configuration: config)
        self.cache = cache
        self.logger = logger
        
        self.jsonDecoder = JSONDecoder()
        self.jsonDecoder.dateDecodingStrategy = .iso8601
    }
    
    // MARK: - Main Request Method with Full Error Handling
    nonisolated func request<T: Codable>(
        _ networkRequest: NetworkRequest,
        useCache: Bool = true
    ) async throws -> T {
        // Check cache first
        if useCache {
            let cacheKey = networkRequest.url.absoluteString
            if let cached: T = cache.getCached(for: cacheKey) {
                logger.log("Cache hit for \(cacheKey)", level: .debug)
                return cached
            }
        }
        
        // Execute request with retry logic
        var lastError: NetworkError = .unknown(NSError(domain: "Unknown", code: 0))
        
        for attempt in 0...networkRequest.retryPolicy.maxRetries {
            do {
                logger.log("Attempt \(attempt + 1) for \(networkRequest.url.absoluteString)", level: .debug)
                
                let response = try await performRequest(networkRequest)
                let data = try validateResponse(response)
                
                let decodedObject = try jsonDecoder.decode(T.self, from: data)
                
                // Cache successful response
                if useCache {
                    cache.cache(decodedObject, for: networkRequest.url.absoluteString)
                }
                
                logger.log("Success: \(networkRequest.url.absoluteString)", level: .debug)
                return decodedObject
                
            } catch let error as NetworkError {
                lastError = error
                
                // Check if error is retryable
                if !isRetryable(error) || attempt >= networkRequest.retryPolicy.maxRetries {
                    logger.log("Non-retryable error or max retries reached: \(error)", level: .error)
                    throw error
                }
                
                // Calculate backoff delay
                let delay = networkRequest.retryPolicy.initialDelay *
                    pow(networkRequest.retryPolicy.backoffMultiplier, Double(attempt))
                
                logger.log("Retrying after \(delay)s (attempt \(attempt + 1))", level: .warning)
                
                try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                
            } catch {
                let networkError = NetworkError.unknown(error)
                logger.log("Unexpected error: \(error)", level: .error)
                throw networkError
            }
        }
        
        throw lastError
    }
    
    // MARK: - Request with Progress Tracking
    nonisolated func requestWithProgress<T: Codable>(
        _ networkRequest: NetworkRequest,
        progressHandler: @escaping (Double) -> Void
    ) async throws -> T {
        var urlRequest = URLRequest(url: networkRequest.url)
        urlRequest.httpMethod = networkRequest.method.rawValue
        urlRequest.timeoutInterval = networkRequest.timeoutInterval
        
        if let headers = networkRequest.headers {
            for (key, value) in headers {
                urlRequest.setValue(value, forHTTPHeaderField: key)
            }
        }
        
        if let body = networkRequest.body {
            urlRequest.httpBody = body
        }
        
        let (data, response) = try await session.data(for: urlRequest)
        _ = try validateResponse((data, response))
        
        let decodedObject = try jsonDecoder.decode(T.self, from: data)
        progressHandler(1.0)
        
        return decodedObject
    }
    
    // MARK: - Private Helper Methods
    private nonisolated func performRequest(_ networkRequest: NetworkRequest) async throws -> (Data, URLResponse) {
        var urlRequest = URLRequest(url: networkRequest.url)
        urlRequest.httpMethod = networkRequest.method.rawValue
        urlRequest.timeoutInterval = networkRequest.timeoutInterval
        
        // Add default headers
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // Add custom headers
        if let headers = networkRequest.headers {
            for (key, value) in headers {
                urlRequest.setValue(value, forHTTPHeaderField: key)
            }
        }
        
        // Add body
        if let body = networkRequest.body {
            urlRequest.httpBody = body
        }
        
        do {
            let (data, response) = try await session.data(for: urlRequest)
            return (data, response)
        } catch URLError.timedOut {
            throw NetworkError.timeout
        } catch URLError.notConnectedToInternet, URLError.networkConnectionLost {
            throw NetworkError.noInternet
        } catch {
            throw NetworkError.unknown(error)
        }
    }
    
    private nonisolated func validateResponse(_ response: (Data, URLResponse)) throws -> Data {
        let (data, urlResponse) = response
        
        guard let httpResponse = urlResponse as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            return data
        case 400...499:
            logger.log("Client error \(httpResponse.statusCode)", level: .warning)
            throw NetworkError.serverError(httpResponse.statusCode)
        case 500...599:
            logger.log("Server error \(httpResponse.statusCode)", level: .error)
            throw NetworkError.serverError(httpResponse.statusCode)
        default:
            throw NetworkError.serverError(httpResponse.statusCode)
        }
    }
    
    private nonisolated func isRetryable(_ error: NetworkError) -> Bool {
        switch error {
        case .timeout, .noInternet:
            return true
        case .serverError(let code):
            return code >= 500 // Retry on server errors only
        case .invalidURL, .invalidResponse, .decodingError:
            return false
        case .unknown:
            return false
        }
    }
    
    // MARK: - Convenience Methods
    nonisolated func fetchJSON<T: Codable>(
        from url: URL,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = NetworkRequest(
            url: url,
            method: .get,
            headers: headers
        )
        return try await request(request)
    }
    
    nonisolated func postJSON<T: Codable>(
        to url: URL,
        body: Encodable,
        headers: [String: String]? = nil
    ) async throws -> T {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let bodyData = try encoder.encode(body)
        
        let request = NetworkRequest(
            url: url,
            method: .post,
            headers: headers,
            body: bodyData
        )
        return try await request(request)
    }
    
    nonisolated func clearCache() {
        cache.clearAllCache()
    }
}

// MARK: - Network Logger
class NetworkLogger {
    enum LogLevel: String {
        case debug = "🔍 DEBUG"
        case info = "ℹ️ INFO"
        case warning = "⚠️ WARNING"
        case error = "❌ ERROR"
    }
    
    private let queue = DispatchQueue(label: "com.network.logger", attributes: .concurrent)
    
    func log(_ message: String, level: LogLevel = .info) {
        queue.async {
            let timestamp = ISO8601DateFormatter().string(from: Date())
            print("[\(timestamp)] \(level.rawValue): \(message)")
        }
    }
}

// MARK: - Swift Concurrency (Structured Concurrency)
extension NetworkManager {
    /// Performs multiple concurrent requests with proper error handling
    nonisolated func fetchMultiple<T: Codable>(
        urls: [URL]
    ) async throws -> [T] {
        return try await withThrowingTaskGroup(of: T.self) { group in
            for url in urls {
                let request = NetworkRequest(url: url)
                group.addTask {
                    return try await self.request(request)
                }
            }
            
            var results: [T] = []
            for try await result in group {
                results.append(result)
            }
            return results
        }
    }
}

// MARK: - Example Usage Patterns
/*
 
// Basic GET request
let url = URL(string: "https://api.example.com/users")!
let users: [User] = try await NetworkManager.shared.fetchJSON(from: url)

// POST with custom retry policy
let postURL = URL(string: "https://api.example.com/login")!
let loginData = LoginRequest(username: "user", password: "pass")
let response: LoginResponse = try await NetworkManager.shared.postJSON(
    to: postURL,
    body: loginData
)

// Custom request with headers and retry policy
var request = NetworkRequest(
    url: URL(string: "https://api.example.com/protected")!,
    method: .get,
    headers: ["Authorization": "Bearer token"],
    retryPolicy: .aggressive
)
let protected: ProtectedData = try await NetworkManager.shared.request(request)

// Multiple concurrent requests
let urls = [URL(string: "https://api.example.com/users")!]
let allUsers: [[User]] = try await NetworkManager.shared.fetchMultiple(urls: urls)

*/
