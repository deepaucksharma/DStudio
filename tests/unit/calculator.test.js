// Unit tests for calculator functions

describe('Latency Calculator', () => {
  let calculator;
  
  beforeEach(() => {
    // Mock DOM elements
    document.body.innerHTML = `
      <div id="latency-calculator">
        <input id="distance" value="1000">
        <select id="medium">
          <option value="fiber" selected>Fiber Optic</option>
        </select>
        <input id="hops" value="5">
        <div id="prop-delay"></div>
        <div id="proc-delay"></div>
        <div id="total-rtt"></div>
      </div>
    `;
    
    // Initialize calculator
    calculator = {
      speedOfLight: {
        fiber: 200000,
        copper: 200000,
        wireless: 300000
      },
      
      calculatePropagationDelay(distance, medium) {
        const speed = this.speedOfLight[medium];
        return (distance / speed) * 1000; // Convert to ms
      },
      
      calculateProcessingDelay(hops) {
        return hops * 0.5; // 0.5ms per hop
      },
      
      calculateRTT(propagation, processing) {
        return (propagation + processing) * 2;
      }
    };
  });
  
  test('calculates propagation delay correctly', () => {
    const delay = calculator.calculatePropagationDelay(1000, 'fiber');
    expect(delay).toBe(5); // 1000km / 200000km/s * 1000 = 5ms
  });
  
  test('calculates processing delay correctly', () => {
    const delay = calculator.calculateProcessingDelay(5);
    expect(delay).toBe(2.5); // 5 hops * 0.5ms = 2.5ms
  });
  
  test('calculates RTT correctly', () => {
    const propagation = 5;
    const processing = 2.5;
    const rtt = calculator.calculateRTT(propagation, processing);
    expect(rtt).toBe(15); // (5 + 2.5) * 2 = 15ms
  });
  
  test('handles different mediums', () => {
    expect(calculator.calculatePropagationDelay(3000, 'wireless')).toBe(10);
    expect(calculator.calculatePropagationDelay(3000, 'fiber')).toBe(15);
  });
  
  test('validates input ranges', () => {
    expect(() => calculator.calculatePropagationDelay(-100, 'fiber')).toThrow();
    expect(() => calculator.calculateProcessingDelay(-1)).toThrow();
  });
});

describe('Capacity Planner', () => {
  let planner;
  
  beforeEach(() => {
    planner = {
      calculateRequiredCapacity(users, requestsPerUser, sizePerRequest) {
        return users * requestsPerUser * sizePerRequest;
      },
      
      calculateServers(totalCapacity, serverCapacity, redundancyFactor = 1.5) {
        return Math.ceil((totalCapacity / serverCapacity) * redundancyFactor);
      },
      
      calculateCost(servers, costPerServer) {
        return servers * costPerServer;
      }
    };
  });
  
  test('calculates required capacity', () => {
    const capacity = planner.calculateRequiredCapacity(1000, 10, 1024);
    expect(capacity).toBe(10240000); // 10MB total
  });
  
  test('calculates server count with redundancy', () => {
    const servers = planner.calculateServers(100, 25, 1.5);
    expect(servers).toBe(6); // ceil((100/25) * 1.5) = 6
  });
  
  test('calculates total cost', () => {
    const cost = planner.calculateCost(6, 1000);
    expect(cost).toBe(6000);
  });
});

describe('Failure Calculator', () => {
  let calculator;
  
  beforeEach(() => {
    calculator = {
      calculateAvailability(uptime, totalTime) {
        return uptime / totalTime;
      },
      
      calculateMTTF(failures, operationalTime) {
        return operationalTime / failures;
      },
      
      calculateMTTR(repairTime, repairs) {
        return repairTime / repairs;
      },
      
      calculateSystemAvailability(mttf, mttr) {
        return mttf / (mttf + mttr);
      },
      
      calculateParallelAvailability(availabilities) {
        return 1 - availabilities.reduce((acc, a) => acc * (1 - a), 1);
      }
    };
  });
  
  test('calculates basic availability', () => {
    const availability = calculator.calculateAvailability(8760, 8766); // 6 hours downtime per year
    expect(availability).toBeCloseTo(0.99932, 5);
  });
  
  test('calculates MTTF correctly', () => {
    const mttf = calculator.calculateMTTF(10, 87600); // 10 failures in 10 years
    expect(mttf).toBe(8760); // 1 year between failures
  });
  
  test('calculates parallel system availability', () => {
    const systemAvailability = calculator.calculateParallelAvailability([0.99, 0.99, 0.99]);
    expect(systemAvailability).toBeCloseTo(0.999999, 6); // Six nines
  });
});