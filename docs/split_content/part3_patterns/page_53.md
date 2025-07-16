Page 53: Edge & IoT
Computing at the speed of physics
THE PROBLEM
Centralized cloud means:
- High latency to edge devices
- Bandwidth costs
- Single point of failure
- Privacy concerns
- Offline scenarios broken
THE SOLUTION
Push compute to the edge:

IoT Device → Edge Node → Regional Hub → Cloud
    ↓           ↓             ↓            ↓
  Instant    <10ms        <50ms       <200ms
  Response   Process     Aggregate    Archive
Edge Architecture Patterns:
1. FOG COMPUTING
   Devices → Fog Nodes → Cloud
   (Sensors) (Gateways)  (Analytics)

2. MOBILE EDGE COMPUTING
   Phone → 5G Tower Edge → Core Network
          (GPU inference)

3. CDN EDGE COMPUTE
   User → Edge PoP → Origin
         (Lambda@Edge)

4. INDUSTRIAL IoT
   Sensors → PLC → Edge Server → Cloud
           (Real-time) (ML)    (History)
PSEUDO CODE IMPLEMENTATION
EdgeNode:
    local_model = null
    cloud_sync_interval = 300s
    
    process_device_data(data):
        // Local inference
        if requires_ml_inference(data):
            if not local_model:
                local_model = download_model()
            result = local_model.predict(data)
        
        // Edge aggregation
        aggregate_locally(data)
        
        // Selective sync
        if is_anomaly(result) or is_scheduled_sync():
            sync_to_cloud(get_aggregated_data())
            
        return result

DeviceManager:
    handle_device_connection(device):
        // Device authentication
        if not verify_device_cert(device):
            return reject_connection()
            
        // Firmware updates
        if device.firmware < latest_version:
            schedule_ota_update(device)
            
        // Twin synchronization
        device_twin = get_device_twin(device.id)
        sync_device_state(device, device_twin)

EdgeCloudSync:
    sync_strategy:
        - Immediate: Safety critical data
        - Batched: Telemetry (every 5 min)
        - On-demand: Logs (when requested)
        - Never: Private data (edge only)
    
    handle_network_partition():
        // Store and forward
        buffer_data_locally()
        set_degraded_mode()
        
        on_reconnect:
            replay_buffered_data()
            reconcile_conflicts()
Edge-Specific Challenges:
1. RESOURCE CONSTRAINTS
   EdgeOptimizer:
       - Quantize ML models (32-bit → 8-bit)
       - Prune unused model layers
       - Compile to edge hardware (TPU/GPU)
       - Swap models based on available memory

2. INTERMITTENT CONNECTIVITY
   ReliableEdgeProtocol:
       - DTN (Delay Tolerant Networking)
       - Store-and-forward queues
       - Conflict-free replicated data
       - Eventual consistency by design

3. SECURITY AT EDGE
   EdgeSecurity:
       - Hardware root of trust (TPM)
       - Secure boot chain
       - Encrypted storage
       - Remote attestation
✓ CHOOSE THIS WHEN:

Latency requirements <50ms
Bandwidth costs prohibitive
Privacy/regulatory requirements
Offline operation needed
Real-time processing required

⚠️ BEWARE OF:

Device management complexity
Security attack surface
Update orchestration
Limited edge resources
Debugging distributed edge

REAL EXAMPLES

Tesla: Autopilot edge inference
Amazon Go: Store edge processing
Industrial: Predictive maintenance
