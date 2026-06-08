import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyFeatureRoutingEngineComponent } from './jrny-feature-routing-engine.component';

describe('JrnyFeatureRoutingEngineComponent', () => {
  let component: JrnyFeatureRoutingEngineComponent;
  let fixture: ComponentFixture<JrnyFeatureRoutingEngineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyFeatureRoutingEngineComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyFeatureRoutingEngineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
